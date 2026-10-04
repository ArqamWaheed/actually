import datetime as dt
import os
from functools import lru_cache
from pathlib import Path

import pandas as pd
import sentry_sdk
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

load_dotenv()

from app import db, observability  # noqa: E402
from app.forecast import MIN_ROWS, Forecaster, load_history, task_rows  # noqa: E402
from app.parser import default_parser  # noqa: E402
from app.plan import make_plan  # noqa: E402
from app.schema import Forecast  # noqa: E402

observability.init()
app = FastAPI(title="Actually")
ROOT = Path(__file__).resolve().parent.parent
PROFILES = {
    "demo": ROOT / "data/demo/tasks_demo.csv",  # synthetic, labelled as such in the UI
    "friend": ROOT / "data/private/tasks.csv",  # real; behind APP_PASSPHRASE
}


def check_profile(profile: str, passphrase: str | None):
    if profile not in PROFILES:
        raise HTTPException(404, "unknown profile")
    if profile != "demo" and passphrase != os.getenv("APP_PASSPHRASE"):
        raise HTTPException(401, "wrong passphrase")


@lru_cache(maxsize=4)
def forecaster(profile: str, n_logged: int) -> Forecaster:
    hist = load_history(str(PROFILES[profile]))
    extra = db.logged_rows(profile)
    if len(extra):
        hist = pd.concat([hist, extra[hist.columns.intersection(extra.columns)]], ignore_index=True)
    if len(hist) < MIN_ROWS:
        raise HTTPException(400, f"need at least {MIN_ROWS} past tasks, have {len(hist)}")
    return Forecaster(hist)


class DumpIn(BaseModel):
    text: str
    free_min: int = 180
    profile: str = "demo"


class LogIn(BaseModel):
    profile: str = "demo"
    open_id: int | None = None
    task: str
    kind: str
    guess_min: int | None = None
    actual_min: int
    done_same_day: bool = True
    dreaded: bool = False
    left_house: bool = False


@app.post("/api/plan")
def plan(body: DumpIn, x_passphrase: str | None = Header(default=None)):
    check_profile(body.profile, x_passphrase)
    with observability.agent_span():
        parsed = default_parser().parse(body.text)
        if parsed.tasks is None or not parsed.tasks.tasks:
            raise HTTPException(422, "couldn't find tasks in that, try listing them with commas")
        tasks = parsed.tasks.tasks
        with observability.tool_span("tabpfn_forecast"):
            fc = forecaster(body.profile, len(db.logged_rows(body.profile)))
            rows = task_rows(tasks)
            pred = fc.predict(rows)
            sentry_sdk.set_tag("tabpfn.fit_mode", fc.fit_mode)
        forecasts = [
            Forecast(title=t.title, kind=t.kind, guess_min=t.guess_min,
                     p50_min=round(float(pred["p50"][i]), 1), p10_min=round(float(pred["p10"][i]), 1),
                     p90_min=round(float(pred["p90"][i]), 1),
                     p_done_today=None if pred["p_done"][i] is None else round(float(pred["p_done"][i]), 2),
                     why=fc.why(rows.iloc[i]))
            for i, t in enumerate(tasks)
        ]
        for f in forecasts:
            f.swallow_risk = f.p90_min >= 0.5 * body.free_min
        db.remember(body.profile, tasks)
        p = make_plan(forecasts, [t.deadline for t in tasks], [t.optional for t in tasks], body.free_min)
    return {"plan": p, "parse_latency_s": round(parsed.latency_s, 2), "history_rows": len(fc.history)}


@app.post("/api/log")
def log(body: LogIn, x_passphrase: str | None = Header(default=None)):
    check_profile(body.profile, x_passphrase)
    now = dt.datetime.now()
    db.log_task(body.profile, {
        "date": now.date().isoformat(), "task": body.task, "kind": body.kind, "guess_min": body.guess_min,
        "actual_min": body.actual_min, "done_same_day": int(body.done_same_day), "start_hour": now.hour,
        "dreaded": int(body.dreaded), "left_house": int(body.left_house), "has_deadline": 0,
    })
    if body.open_id is not None:
        db.close_task(body.profile, body.open_id)
    return {"ok": True, "history_rows": len(load_history(str(PROFILES[body.profile]))) + len(db.logged_rows(body.profile))}


@app.get("/api/open")
def open_list(profile: str = "demo", x_passphrase: str | None = Header(default=None)):
    check_profile(profile, x_passphrase)
    return {"open": db.open_tasks(profile)}


@app.get("/api/health")
def health():
    return {"ok": True, "parser_backend": os.getenv("PARSER_BACKEND", "ollama"),
            "friend_ready": PROFILES["friend"].exists()}


@app.get("/")
def index():
    return FileResponse(ROOT / "app/static/index.html")

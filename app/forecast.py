"""TabPFN on the friend's own task history.

Regressor: how long a task will actually take him (median + 10-90% range).
Classifier: probability he finishes it the day he planned it.
Both are in-context: every logged task improves the next prediction with no retraining.
"""
from __future__ import annotations

import datetime as dt
import math

import numpy as np
import pandas as pd

FEATURES = ["kind", "guess_min", "start_hour", "day_of_week", "dreaded", "left_house", "has_deadline"]
MIN_ROWS = 12


def load_history(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    for c in ("dreaded", "left_house", "done_same_day"):
        if c in df:
            df[c] = df[c].astype(str).str.strip().str.lower().isin(["y", "yes", "1", "true"]).astype(int)
    if "date" in df:
        df["day_of_week"] = pd.to_datetime(df["date"], errors="coerce").dt.dayofweek
    df["has_deadline"] = df.get("has_deadline", 0)
    df = df[pd.to_numeric(df["actual_min"], errors="coerce").notna()].copy()
    df["actual_min"] = df["actual_min"].astype(float)
    df["guess_min"] = pd.to_numeric(df["guess_min"], errors="coerce")
    return df


def task_rows(tasks, now: dt.datetime | None = None) -> pd.DataFrame:
    now = now or dt.datetime.now()
    return pd.DataFrame([{
        "kind": t.kind,
        "guess_min": t.guess_min if t.guess_min is not None else np.nan,
        "start_hour": now.hour,
        "day_of_week": now.weekday(),
        "dreaded": int(t.dreaded),
        "left_house": int(t.must_leave_house),
        "has_deadline": int(t.deadline is not None),
    } for t in tasks])


class Forecaster:
    def __init__(self, history: pd.DataFrame):
        from tabpfn import TabPFNClassifier, TabPFNRegressor

        self.history = history
        X = history[FEATURES]
        # log-duration: durations are right-skewed; TabPFN is happier on the log scale
        self.reg = TabPFNRegressor().fit(X, np.log1p(history["actual_min"]))
        self.clf = None
        y = history.get("done_same_day")
        if y is not None and y.nunique() == 2:
            self.clf = TabPFNClassifier().fit(X, y)
        self.overrun = float(np.nanmedian(history["actual_min"] / history["guess_min"]))

    def predict(self, rows: pd.DataFrame) -> dict:
        q = self.reg.predict(rows[FEATURES], output_type="quantiles", quantiles=[0.1, 0.5, 0.9])
        p10, p50, p90 = (np.expm1(np.asarray(a)) for a in q)
        p_done = self.clf.predict_proba(rows[FEATURES])[:, 1] if self.clf is not None else [None] * len(rows)
        return {"p10": p10, "p50": p50, "p90": p90, "p_done": p_done}

    def why(self, row: pd.Series) -> list[str]:
        """Plain-English drivers from the friend's own history (cheap, deterministic).
        Shapley attributions (tabpfn-extensions) are computed offline in eval/ for the post."""
        h, out = self.history, []
        same = h[h["kind"] == row["kind"]]
        if len(same) >= 3 and same["guess_min"].notna().any():
            r = float(np.nanmedian(same["actual_min"] / same["guess_min"]))
            if math.isfinite(r) and r > 1.2:
                if np.isnan(row["guess_min"]):
                    out.append(f"{row['kind']} tasks usually run ~{r:.1f}x longer than you plan")
                else:
                    out.append(f"{row['kind']} tasks take you ~{r:.1f}x your guess")
        if row["dreaded"] and h["dreaded"].sum() >= 3:
            d = h.groupby("dreaded")["actual_min"].median()
            if 1 in d and 0 in d and d[1] > d[0]:
                out.append(f"dreaded tasks run ~{d[1] / d[0]:.1f}x longer for you")
        late = h[h["start_hour"] >= 21]
        if row["start_hour"] >= 21 and len(late) >= 3 and "done_same_day" in h:
            out.append(f"you finish only {late['done_same_day'].mean():.0%} of tasks started after 9 PM")
        return out[:3]

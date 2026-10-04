"""Latency of the TabPFN forecast tool, per fit_mode (the bug Sentry surfaced).
Usage: python -m eval.bench_forecast"""
import json
import statistics
import time

from app.forecast import Forecaster, load_history, task_rows
from app.schema import Task

hist = load_history("data/demo/tasks_demo.csv")
tasks = [Task(title=t, kind=k, guess_min=g) for t, k, g in
         [("email sir", "admin", 5), ("dbms assignment", "study", 30), ("laundry", "chore", None),
          ("call nani", "social", None), ("gym", "health", None), ("reply hamza", "social", None)]]
out = {}
for mode in ["fit_preprocessors", "fit_with_cache"]:
    import os
    os.environ["TABPFN_FIT_MODE"] = mode
    t0 = time.perf_counter(); fc = Forecaster(hist); fit_s = time.perf_counter() - t0
    lat = []
    for _ in range(6):
        t0 = time.perf_counter(); fc.predict(task_rows(tasks)); lat.append(time.perf_counter() - t0)
    out[mode] = {"fit_s": round(fit_s, 2), "predict_p50_s": round(statistics.median(lat[1:]), 2)}
    print(mode, out[mode])
json.dump(out, open("results/bench_forecast.json", "w"), indent=2)

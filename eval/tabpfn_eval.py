"""Headline eval: does TabPFN predict how long his tasks take better than he does?

Repeated K-fold CV on the task history. Baselines: his own guess, "x2" rule, his-median-overrun x guess,
linear regression. Usage: python -m eval.tabpfn_eval --csv data/private/tasks.csv --label friend
"""
import argparse
import json

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import RepeatedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder

from app.forecast import FEATURES, load_history


def metrics(y, p):
    y, p = np.asarray(y), np.asarray(p)
    return {"mae_min": float(np.mean(np.abs(y - p))), "within_25pct": float(np.mean(np.abs(p - y) <= 0.25 * y))}


def main():
    from tabpfn import TabPFNRegressor

    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--label", default="demo")
    ap.add_argument("--repeats", type=int, default=3)
    a = ap.parse_args()
    df = load_history(a.csv)
    df = df[df["guess_min"].notna()].reset_index(drop=True)
    X, y = df[FEATURES], df["actual_min"].values
    preds = {k: np.zeros((a.repeats, len(df))) for k in ["his_guess", "x2_rule", "his_overrun", "linear", "tabpfn"]}
    lin = make_pipeline(
        ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore"), ["kind"])], remainder="passthrough"),
        SimpleImputer(), LinearRegression())
    rkf = RepeatedKFold(n_splits=5, n_repeats=a.repeats, random_state=0)
    for j, (tr, te) in enumerate(rkf.split(X)):
        r = j // 5
        g = df.loc[te, "guess_min"].values
        preds["his_guess"][r, te] = g
        preds["x2_rule"][r, te] = 2 * g
        ratio = np.nanmedian(y[tr] / df.loc[tr, "guess_min"].values)
        preds["his_overrun"][r, te] = ratio * g
        preds["linear"][r, te] = np.expm1(lin.fit(X.iloc[tr], np.log1p(y[tr])).predict(X.iloc[te]))
        m = TabPFNRegressor().fit(X.iloc[tr], np.log1p(y[tr]))
        preds["tabpfn"][r, te] = np.expm1(m.predict(X.iloc[te], output_type="median"))
    res = {}
    for k, P in preds.items():
        per = [metrics(y, P[r]) for r in range(a.repeats)]
        res[k] = {m: float(np.mean([p[m] for p in per])) for m in per[0]}
    out = {"label": a.label, "n_tasks": len(df), "results": res}
    print(json.dumps(out, indent=2))
    with open(f"results/tabpfn_eval_{a.label}.json", "w") as f:
        json.dump(out, f, indent=2)
    names = {"his_guess": "His own guess", "x2_rule": '"Double it" rule', "his_overrun": "His guess x his median overrun",
             "linear": "Linear regression", "tabpfn": "**TabPFN**"}
    lines = ["| Estimator | MAE (min) | within ±25% |", "|---|---|---|"]
    lines += [f"| {names[k]} | {v['mae_min']:.1f} | {v['within_25pct']:.0%} |" for k, v in res.items()]
    open(f"results/tabpfn_eval_{a.label}.md", "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()

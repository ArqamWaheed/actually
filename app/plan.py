"""Fit forecast tasks into the free time he actually has."""
from app.schema import Forecast, Plan

DEADLINE_RANK = {"today": 0, "tomorrow": 1, "this_week": 2, None: 3}


def make_plan(forecasts: list[Forecast], deadlines: list, optional: list[bool], free_min: int) -> Plan:
    order = sorted(range(len(forecasts)),
                   key=lambda i: (optional[i], DEADLINE_RANK.get(deadlines[i], 3), forecasts[i].p50_min))
    do_now, move, used = [], [], 0.0
    for i in order:
        f = forecasts[i]
        if used + f.p50_min <= free_min:
            do_now.append(f)
            used += f.p50_min
        else:
            move.append(f)
    return Plan(
        free_min=free_min,
        guessed_total_min=sum(f.guess_min or 0 for f in forecasts),
        actual_total_min=round(sum(f.p50_min for f in forecasts), 1),
        do_now=do_now,
        move=move,
    )

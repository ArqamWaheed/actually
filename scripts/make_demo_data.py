"""SYNTHETIC demo profile for the public live demo. Not the friend's data, and labelled as such in the UI.

Generative story (so TabPFN has real structure to find): admin/dreaded/late-night tasks overrun more.
"""
import csv
import datetime as dt
import random
from pathlib import Path

random.seed(7)
TASKS = {
    "admin": ["email prof about extension", "fill scholarship form", "reply to landlord", "pay internet bill",
              "book dentist", "renew cnic appointment"],
    "study": ["dbms assignment", "revise os chapter 4", "finish lab report", "watch lecture 7", "past paper q3"],
    "chore": ["laundry", "clean room", "dishes", "fold clothes"],
    "errand": ["groceries", "pick up parcel", "print notes"],
    "social": ["call ammi back", "reply to group chat", "birthday msg for hamza"],
    "creative": ["edit reel", "sketch logo idea"],
    "work": ["update resume", "fix freelance bug"],
    "health": ["gym", "go for a walk"],
}
BASE = {"admin": 15, "study": 60, "chore": 30, "errand": 40, "social": 15, "creative": 45, "work": 50, "health": 50}
OVERRUN = {"admin": 2.6, "study": 1.7, "chore": 1.3, "errand": 1.5, "social": 1.8, "creative": 2.0, "work": 1.9,
           "health": 1.2}

out = Path(__file__).resolve().parent.parent / "data/demo/tasks_demo.csv"
out.parent.mkdir(parents=True, exist_ok=True)
start = dt.date(2026, 9, 10)
with out.open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["date", "task", "kind", "guess_min", "actual_min", "done_same_day", "start_hour", "dreaded",
                "left_house"])
    for i in range(70):
        kind = random.choice(list(TASKS))
        day = start + dt.timedelta(days=i // 3)
        hour = random.choice([10, 12, 14, 16, 18, 20, 22, 23])
        dreaded = kind in ("admin", "study") and random.random() < 0.6
        left = kind in ("errand", "health")
        guess = int(BASE[kind] * random.uniform(0.6, 1.2) / 5) * 5 or 5
        mult = OVERRUN[kind] * (1.5 if dreaded else 1) * (1.3 if hour >= 21 else 1) * random.lognormvariate(0, 0.25)
        actual = max(5, round(guess * mult))
        done = int(random.random() > (0.25 + 0.3 * dreaded + 0.25 * (hour >= 21)))
        w.writerow([day.isoformat(), random.choice(TASKS[kind]), kind, guess, actual, "y" if done else "n", hour,
                    "y" if dreaded else "n", "y" if left else "n"])
print("wrote", out)

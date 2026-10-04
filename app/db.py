"""SQLite on the host box: logged tasks become new TabPFN context rows."""
import os
import sqlite3

DB_PATH = os.getenv("DB_PATH", "actually.db")


def conn():
    c = sqlite3.connect(DB_PATH)
    c.execute("""CREATE TABLE IF NOT EXISTS logged (
        id INTEGER PRIMARY KEY, profile TEXT, date TEXT, task TEXT, kind TEXT, guess_min REAL,
        actual_min REAL, done_same_day INTEGER, start_hour INTEGER, dreaded INTEGER, left_house INTEGER,
        has_deadline INTEGER)""")
    c.execute("""CREATE TABLE IF NOT EXISTS open_tasks (
        id INTEGER PRIMARY KEY, profile TEXT, title TEXT, kind TEXT, guess_min REAL, dreaded INTEGER,
        created_at TEXT, done_at TEXT)""")
    return c


def log_task(profile: str, row: dict):
    with conn() as c:
        c.execute("""INSERT INTO logged (profile,date,task,kind,guess_min,actual_min,done_same_day,start_hour,
                     dreaded,left_house,has_deadline) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                  (profile, row["date"], row["task"], row["kind"], row.get("guess_min"), row["actual_min"],
                   row.get("done_same_day", 1), row["start_hour"], row.get("dreaded", 0),
                   row.get("left_house", 0), row.get("has_deadline", 0)))


def logged_rows(profile: str):
    import pandas as pd

    with conn() as c:
        return pd.read_sql_query("SELECT * FROM logged WHERE profile = ?", c, params=(profile,))


def remember(profile: str, tasks) -> None:
    """Out of sight is out of mind: every task from a dump stays listed until it is marked done."""
    import datetime as dt
    from difflib import SequenceMatcher

    with conn() as c:
        open_titles = [r[0] for r in c.execute(
            "SELECT title FROM open_tasks WHERE profile=? AND done_at IS NULL", (profile,))]
        for t in tasks:
            if any(SequenceMatcher(None, t.title.lower(), o.lower()).ratio() > 0.8 for o in open_titles):
                continue
            c.execute("INSERT INTO open_tasks (profile,title,kind,guess_min,dreaded,created_at) VALUES (?,?,?,?,?,?)",
                      (profile, t.title, t.kind, t.guess_min, int(t.dreaded), dt.datetime.now().isoformat()))
            open_titles.append(t.title)


def open_tasks(profile: str) -> list[dict]:
    with conn() as c:
        rows = c.execute("SELECT id,title,kind,guess_min,dreaded,created_at FROM open_tasks "
                         "WHERE profile=? AND done_at IS NULL ORDER BY created_at", (profile,)).fetchall()
    return [dict(zip(["id", "title", "kind", "guess_min", "dreaded", "created_at"], r)) for r in rows]


def close_task(profile: str, task_id: int) -> None:
    import datetime as dt

    with conn() as c:
        c.execute("UPDATE open_tasks SET done_at=? WHERE id=? AND profile=?",
                  (dt.datetime.now().isoformat(), task_id, profile))

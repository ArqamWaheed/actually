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

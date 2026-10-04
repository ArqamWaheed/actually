from typing import Literal, Optional

from pydantic import BaseModel, Field

Kind = Literal["admin", "study", "creative", "chore", "errand", "social", "work", "health"]


class Task(BaseModel):
    title: str
    kind: Kind = "admin"
    guess_min: Optional[int] = None
    deadline: Optional[Literal["today", "tomorrow", "this_week"]] = None
    must_leave_house: bool = False
    dreaded: bool = False
    optional: bool = False


class TaskList(BaseModel):
    tasks: list[Task] = Field(default_factory=list)


class Forecast(BaseModel):
    title: str
    kind: str
    guess_min: Optional[int]
    p50_min: float
    p10_min: float
    p90_min: float
    p_done_today: Optional[float]
    why: list[str]
    swallow_risk: bool = False  # p90 could eat half his free time (hyperfocus)


class Plan(BaseModel):
    free_min: int
    guessed_total_min: int
    actual_total_min: float
    do_now: list[Forecast]
    move: list[Forecast]

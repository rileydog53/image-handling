# ─────────────────────────────────────────────
# models.py — Data shapes for the whole app
#
# Pydantic "models" are blueprints that describe exactly what
# data should look like going in and out of each endpoint.
# FastAPI uses these to automatically validate requests and
# build the correct JSON responses.
# ─────────────────────────────────────────────

from pydantic import BaseModel
from typing import List, Literal, Optional


# What the frontend sends to /parse:
# just the raw text the user typed.
class ParseRequest(BaseModel):
    text: str


# What Gemini returns after parsing the text —
# and also what the frontend sends to /create.
# Every field is Optional because the user might be mid-sentence
# and some fields haven't been filled in yet.
class ParsedReminder(BaseModel):
    title: Optional[str] = None          # e.g. "Call mom"
    due_date: Optional[str] = None       # ISO-8601 format: "2026-04-29T15:00:00"
    notes: Optional[str] = None          # any extra detail
    type: Optional[Literal["reminder", "calendar"]] = "reminder"  # reminder or calendar event
    tags: Optional[List[str]] = None     # e.g. ["Family", "Work"]


# CreateRequest is identical to ParsedReminder —
# the frontend just forwards what it got from /parse straight to /create.
class CreateRequest(ParsedReminder):
    pass


# What the server sends back after /create runs.
# success = True means the reminder appeared in Apple Reminders.
class CreateResponse(BaseModel):
    success: bool
    id: Optional[str] = None    # the Apple-assigned reminder ID (if returned)
    error: Optional[str] = None # error message if something went wrong

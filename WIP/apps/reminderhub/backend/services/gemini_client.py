# ─────────────────────────────────────────────
# services/gemini_client.py — AI parsing via Google Gemini
#
# This is the brain of the app. It takes raw text the user typed
# and asks Gemini to extract structured fields from it:
# title, date, notes, type, and tags.
#
# We use "structured output" — meaning Gemini is forced to return
# valid JSON matching our exact schema, rather than free-form text.
# ─────────────────────────────────────────────

import os
from datetime import datetime
from typing import List, Optional

from google import genai
from google.genai.types import GenerateContentConfig
from pydantic import BaseModel

# Lazy-initialized client — only created on first use, then reused.
# This avoids reconnecting to Google on every single request.
_client = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        # The API key is read from the environment (loaded from .env by main.py)
        _client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return _client


# This Pydantic model is the "schema" we send to Gemini.
# It tells Gemini exactly what JSON shape to return.
# Gemini guarantees its response matches this — no parsing errors.
class ParsedReminder(BaseModel):
    title: Optional[str] = None      # what needs to be done
    due_date: Optional[str] = None   # ISO-8601 datetime, e.g. "2026-04-29T15:00:00"
    notes: Optional[str] = None      # extra detail beyond the title
    type: Optional[str] = "reminder" # "reminder" or "calendar"
    tags: Optional[List[str]] = None # category names, e.g. ["Family", "Work"]


# The system instruction is sent to Gemini before the user's text.
# It tells Gemini its role and exactly how to behave.
# {today} is filled in at call time so relative dates ("tomorrow") work correctly.
_SYSTEM_INSTRUCTION = """You extract reminder details from natural language text.
Today's date is {today}. Use this as the anchor for relative dates like "tomorrow" or "next Friday".

Extract:
- title: concise action title (what needs to be done)
- due_date: ISO-8601 datetime string if a date/time is mentioned, otherwise null
- notes: any extra detail not captured in the title, otherwise null
- type: "reminder" for personal tasks/reminders, "calendar" for events with a specific time involving others
- tags: list of category names inferred from the text. Detect tags from:
  * explicit hashtags: #family, #Family, #FAMILY → ["Family"]
  * plain mentions of a category: "family thing", "for work", "grocery run" → ["Family"], ["Work"], ["Groceries"]
  * Always Title Case the tag name (e.g. "family" → "Family", "work stuff" → "Work")
  * Only include tags you are confident about. If no category is apparent, return null.

Return only the JSON object. No prose."""


def parse_reminder(text: str) -> dict:
    # Get today's date to inject into the system prompt.
    today = datetime.now().strftime("%Y-%m-%d")
    client = _get_client()

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",  # free tier: 30 RPM, 1500 req/day
        contents=text,                  # the user's raw input
        config=GenerateContentConfig(
            system_instruction=_SYSTEM_INSTRUCTION.format(today=today),
            response_mime_type="application/json",  # tell Gemini to return JSON
            response_schema=ParsedReminder,         # enforce our exact shape
            temperature=0.1,  # low = more consistent/predictable, less creative
        ),
    )

    # response.parsed gives us the Pydantic object directly (already validated).
    parsed = response.parsed
    if parsed is None:
        # Fallback if Gemini returns something unexpected — return all nulls.
        return {"title": None, "due_date": None, "notes": None, "type": "reminder", "tags": None}

    # Convert the Pydantic object to a plain dict for the rest of the app.
    return parsed.model_dump()

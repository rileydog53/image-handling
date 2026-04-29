import os
from datetime import datetime
from typing import List, Optional

from google import genai
from google.genai.types import GenerateContentConfig
from pydantic import BaseModel

_client = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return _client


class ParsedReminder(BaseModel):
    title: Optional[str] = None
    due_date: Optional[str] = None
    notes: Optional[str] = None
    type: Optional[str] = "reminder"
    tags: Optional[List[str]] = None


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
    today = datetime.now().strftime("%Y-%m-%d")
    client = _get_client()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=text,
        config=GenerateContentConfig(
            system_instruction=_SYSTEM_INSTRUCTION.format(today=today),
            response_mime_type="application/json",
            response_schema=ParsedReminder,
            temperature=0.1,
        ),
    )

    parsed = response.parsed
    if parsed is None:
        return {"title": None, "due_date": None, "notes": None, "type": "reminder", "tags": None}

    return parsed.model_dump()

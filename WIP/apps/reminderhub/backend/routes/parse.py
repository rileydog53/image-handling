# ─────────────────────────────────────────────
# routes/parse.py — The /parse endpoint
#
# The frontend calls this every time the user pauses typing.
# It sends the raw text to Gemini and returns structured fields
# (title, date, tags, etc.) back to the frontend for the preview card.
# ─────────────────────────────────────────────

import asyncio

from fastapi import APIRouter, HTTPException

from models import ParseRequest, ParsedReminder
from services.gemini_client import parse_reminder

router = APIRouter()


@router.post("/parse", response_model=ParsedReminder)
async def parse(req: ParseRequest):
    # If the text box is empty or just whitespace, return a blank reminder
    # rather than wasting an API call to Gemini.
    if not req.text.strip():
        return ParsedReminder()

    try:
        # asyncio.to_thread() runs the Gemini call in a background thread.
        # This is needed because the Gemini SDK is "synchronous" (blocking),
        # but FastAPI is "async" — we can't block the main thread or it
        # would freeze the whole server while waiting for Gemini to respond.
        result = await asyncio.to_thread(parse_reminder, req.text)
        return ParsedReminder(**result)
    except Exception as e:
        # If anything goes wrong (Gemini down, bad response, etc.),
        # send a 500 error back to the frontend with the reason.
        raise HTTPException(status_code=500, detail=str(e))

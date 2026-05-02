# ─────────────────────────────────────────────
# routes/create.py — The /create endpoint
#
# Called when the user hits "Send to Apple" or presses Cmd+Enter.
# Takes the parsed reminder data and hands it off to the
# reminders_handler, which runs the AppleScript to create
# the actual entry in Apple Reminders or Calendar.
# ─────────────────────────────────────────────

import asyncio

from fastapi import APIRouter, HTTPException

from models import CreateRequest, CreateResponse
from services.reminders_handler import create_calendar_event, create_reminder

router = APIRouter()


@router.post("/create", response_model=CreateResponse)
async def create(req: CreateRequest):
    # A title is the minimum we need — refuse if it's missing.
    if not req.title:
        raise HTTPException(status_code=422, detail="title is required")

    try:
        if req.type == "calendar":
            # Create a Calendar event (for things like "lunch with Sarah")
            result = await asyncio.to_thread(
                create_calendar_event, req.title, req.due_date, req.notes
            )
        else:
            # Create an Apple Reminder (the default for most things)
            # Tags are passed so the handler can route it to the right list.
            result = await asyncio.to_thread(
                create_reminder, req.title, req.due_date, req.notes, req.tags
            )
        return CreateResponse(**result)
    except Exception as e:
        # Don't crash — return a clean error message the frontend can display.
        return CreateResponse(success=False, error=str(e))

import asyncio

from fastapi import APIRouter, HTTPException

from models import CreateRequest, CreateResponse
from services.reminders_handler import create_calendar_event, create_reminder

router = APIRouter()


@router.post("/create", response_model=CreateResponse)
async def create(req: CreateRequest):
    if not req.title:
        raise HTTPException(status_code=422, detail="title is required")
    try:
        if req.type == "calendar":
            result = await asyncio.to_thread(
                create_calendar_event, req.title, req.due_date, req.notes
            )
        else:
            result = await asyncio.to_thread(
                create_reminder, req.title, req.due_date, req.notes, req.tags
            )
        return CreateResponse(**result)
    except Exception as e:
        return CreateResponse(success=False, error=str(e))

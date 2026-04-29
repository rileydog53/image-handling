import asyncio

from fastapi import APIRouter, HTTPException

from models import ParseRequest, ParsedReminder
from services.gemini_client import parse_reminder

router = APIRouter()


@router.post("/parse", response_model=ParsedReminder)
async def parse(req: ParseRequest):
    if not req.text.strip():
        return ParsedReminder()
    try:
        result = await asyncio.to_thread(parse_reminder, req.text)
        return ParsedReminder(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

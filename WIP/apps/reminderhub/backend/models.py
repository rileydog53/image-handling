from pydantic import BaseModel
from typing import List, Literal, Optional


class ParseRequest(BaseModel):
    text: str


class ParsedReminder(BaseModel):
    title: Optional[str] = None
    due_date: Optional[str] = None
    notes: Optional[str] = None
    type: Optional[Literal["reminder", "calendar"]] = "reminder"
    tags: Optional[List[str]] = None


class CreateRequest(ParsedReminder):
    pass


class CreateResponse(BaseModel):
    success: bool
    id: Optional[str] = None
    error: Optional[str] = None

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class EventBase(BaseModel):
    title: str
    description: str
    date: datetime
    location: str
    max_participants: Optional[int] = None


class EventCreate(EventBase):
    organizer_id: int


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None
    location: Optional[str] = None
    max_participants: Optional[int] = None


class EventResponse(EventBase):
    id: int
    organizer_id: int
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class EventAttendance(BaseModel):
    user_id: int
    event_id: int
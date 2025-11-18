from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CommentBase(BaseModel):
    content: str
    rating: int


class CommentCreate(CommentBase):
    user_id: int
    event_id: int


class CommentResponse(CommentBase):
    id: int
    user_id: int
    event_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ShareEvent(BaseModel):
    event_id: int
    share_type: str  # 'social_media', 'email'
    recipient: Optional[str] = None
from pydantic import BaseModel, validator, Field
from typing import Optional
from datetime import datetime


class CommentBase(BaseModel):
    content: str
    rating: int = Field(..., ge=1, le=5, description="Rating must be between 1 and 5")

    @validator('rating')
    def validate_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Rating must be between 1 and 5')
        return v


class CommentCreate(CommentBase):
    user_id: int
    event_id: int


class CommentUpdate(BaseModel):
    content: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating must be between 1 and 5")

    @validator('rating')
    def validate_rating(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Rating must be between 1 and 5')
        return v


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


class ShareEventResponse(BaseModel):
    id: int
    event_id: int
    share_type: str
    recipient: Optional[str] = None
    shared_at: datetime

    class Config:
        from_attributes = True

class NotificationResponse(BaseModel):
    event_id: int
    event_title: str
    event_date: datetime
    event_location: str
    notification_type: str
    message: str
    days_until_event: Optional[int] = None
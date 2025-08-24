from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class IdeaBase(BaseModel):
    title: str
    description: str
    angle: Optional[str] = None
    current_event_hook: Optional[str] = None


class IdeaCreate(IdeaBase):
    topic_id: int


class IdeaUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    angle: Optional[str] = None
    current_event_hook: Optional[str] = None
    is_approved: Optional[bool] = None
    is_rejected: Optional[bool] = None
    user_notes: Optional[str] = None


class IdeaResponse(IdeaBase):
    id: int
    topic_id: int
    user_id: int
    prompt_used: Optional[str] = None
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    is_approved: bool
    is_rejected: bool
    user_notes: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class IdeaList(BaseModel):
    ideas: List[IdeaResponse]
    total: int


class IdeaApprovalRequest(BaseModel):
    is_approved: bool
    user_notes: Optional[str] = None

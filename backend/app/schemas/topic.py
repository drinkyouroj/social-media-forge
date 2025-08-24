from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TopicBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    keywords: Optional[List[str]] = None
    target_audience: Optional[str] = None
    idea_count: int = 10
    target_word_count: int = 1000
    persona_id: Optional[int] = None


class TopicCreate(TopicBase):
    pass


class TopicUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    keywords: Optional[List[str]] = None
    target_audience: Optional[str] = None
    idea_count: Optional[int] = None
    target_word_count: Optional[int] = None
    persona_id: Optional[int] = None


class TopicResponse(TopicBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TopicList(BaseModel):
    topics: List[TopicResponse]
    total: int

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SocialPostBase(BaseModel):
    platform: str
    content: str
    hashtags: Optional[List[str]] = None
    mentions: Optional[List[str]] = None
    call_to_action: Optional[str] = None


class SocialPostCreate(SocialPostBase):
    blog_post_id: int


class SocialPostUpdate(BaseModel):
    content: Optional[str] = None
    hashtags: Optional[List[str]] = None
    mentions: Optional[List[str]] = None
    call_to_action: Optional[str] = None
    is_approved: Optional[bool] = None
    user_notes: Optional[str] = None


class SocialPostResponse(SocialPostBase):
    id: int
    blog_post_id: int
    character_count: Optional[int] = None
    is_within_limits: bool = True
    prompt_used: Optional[str] = None
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    is_approved: bool
    user_notes: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SocialPostList(BaseModel):
    social_posts: List[SocialPostResponse]
    total: int

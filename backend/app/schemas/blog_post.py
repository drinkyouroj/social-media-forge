from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class BlogPostBase(BaseModel):
    title: str
    content: str
    excerpt: Optional[str] = None
    word_count: Optional[int] = None
    reading_time: Optional[int] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class BlogPostCreate(BlogPostBase):
    idea_id: int
    persona_id: int


class BlogPostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None
    word_count: Optional[int] = None
    reading_time: Optional[int] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    is_approved: Optional[bool] = None
    user_notes: Optional[str] = None


class BlogPostResponse(BlogPostBase):
    id: int
    idea_id: int
    user_id: int
    persona_id: int
    slug: Optional[str] = None
    is_approved: bool
    user_notes: Optional[str] = None
    user_edits: Optional[List[Dict[str, Any]]] = None
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    generation_duration: Optional[int] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BlogPostList(BaseModel):
    blog_posts: List[BlogPostResponse]
    total: int

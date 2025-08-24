from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class SourceBase(BaseModel):
    url: str
    title: str
    publication: Optional[str] = None
    author: Optional[str] = None
    date_published: Optional[str] = None
    excerpt: Optional[str] = None


class ResearchBase(BaseModel):
    research_prompt: str


class ResearchCreate(ResearchBase):
    idea_id: int


class ResearchUpdate(BaseModel):
    key_findings: Optional[List[str]] = None
    outline: Optional[Dict[str, Any]] = None
    sources: Optional[List[SourceBase]] = None
    source_count: Optional[int] = None
    status: Optional[str] = None


class ResearchResponse(ResearchBase):
    id: int
    idea_id: int
    key_findings: Optional[List[str]] = None
    outline: Optional[Dict[str, Any]] = None
    sources: Optional[List[SourceBase]] = None
    source_count: int = 0
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    research_duration: Optional[int] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ResearchList(BaseModel):
    research: List[ResearchResponse]
    total: int


class ResearchStartRequest(BaseModel):
    idea_id: int
    research_prompt: Optional[str] = None  # If not provided, will be auto-generated

from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class MessageResponse(BaseModel):
    message: str


class StatusResponse(BaseModel):
    status: str
    message: Optional[str] = None
    timestamp: datetime = datetime.utcnow()


class PaginationParams(BaseModel):
    page: int = 1
    size: int = 20
    max_size: int = 100


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int


class FilterParams(BaseModel):
    search: Optional[str] = None
    status: Optional[str] = None
    user_id: Optional[int] = None
    persona_id: Optional[int] = None
    category: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

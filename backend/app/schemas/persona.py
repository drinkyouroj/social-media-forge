from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class PersonaBase(BaseModel):
    name: str
    description: Optional[str] = None
    writing_style: str = "professional"
    tone: str = "neutral"
    target_audience: str = "general"
    include_statistics: bool = True
    include_examples: bool = True
    include_case_studies: bool = False
    include_quotes: bool = False
    always_key_takeaways: bool = True
    include_call_to_action: bool = False
    preferred_section_count: int = 5
    custom_preferences: Dict[str, Any] = {}


class PersonaCreate(PersonaBase):
    pass


class PersonaUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    writing_style: Optional[str] = None
    tone: Optional[str] = None
    target_audience: Optional[str] = None
    include_statistics: Optional[bool] = None
    include_examples: Optional[bool] = None
    include_case_studies: Optional[bool] = None
    include_quotes: Optional[bool] = None
    always_key_takeaways: Optional[bool] = None
    include_call_to_action: Optional[bool] = None
    preferred_section_count: Optional[int] = None
    custom_preferences: Optional[Dict[str, Any]] = None


class PersonaResponse(PersonaBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PersonaList(BaseModel):
    personas: List[PersonaResponse]
    total: int

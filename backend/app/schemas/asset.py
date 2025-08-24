from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class AssetBase(BaseModel):
    asset_type: str
    title: Optional[str] = None
    description: Optional[str] = None
    prompt_used: Optional[str] = None
    model_used: Optional[str] = None
    generation_parameters: Optional[Dict[str, Any]] = None


class AssetCreate(AssetBase):
    blog_post_id: int


class AssetUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    prompt_used: Optional[str] = None
    model_used: Optional[str] = None
    generation_parameters: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    error_message: Optional[str] = None


class AssetResponse(AssetBase):
    id: int
    blog_post_id: int
    file_url: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    generation_duration: Optional[int] = None
    api_cost: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AssetList(BaseModel):
    assets: list[AssetResponse]
    total: int

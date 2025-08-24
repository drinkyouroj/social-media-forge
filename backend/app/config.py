from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    # App settings
    app_name: str = "Social Media Forge"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/forge"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Security
    session_secret: str = "change-me-in-production"
    session_expire_hours: int = 24
    
    # AI API Keys
    openai_api_key: str
    anthropic_api_key: str
    freepik_api_key: str
    
    # Admin user
    admin_email: str = "admin@example.com"
    admin_password: str = "JustinIsNotReallySocial%789"
    
    # Source filtering
    allowed_source_mode: str = "whitelist"  # whitelist, blacklist, or allow_all
    allowed_sources: List[str] = [
        "bbc.com", "cnn.com", "reuters.com", "apnews.com", 
        "nytimes.com", "wsj.com", "ft.com", "techcrunch.com", 
        "theverge.com", "wired.com"
    ]
    
    # AI settings
    openai_model: str = "gpt-4o"
    anthropic_model: str = "claude-3-sonnet-20240229"
    
    # Job queue settings
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

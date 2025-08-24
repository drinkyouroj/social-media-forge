from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    blog_post_id = Column(Integer, ForeignKey("blog_posts.id"), nullable=False)
    
    # Asset details
    asset_type = Column(String(50), nullable=False)  # image, video, etc.
    title = Column(String(255))
    description = Column(Text)
    
    # File information
    file_url = Column(String(500))
    file_path = Column(String(500))
    file_size = Column(Integer)  # in bytes
    mime_type = Column(String(100))
    
    # Generation metadata
    prompt_used = Column(Text)
    model_used = Column(String(100))  # freepik-flux-dev, etc.
    generation_parameters = Column(JSON, default=dict)  # aspect_ratio, styling, etc.
    
    # Status
    status = Column(String(50), default="pending")  # pending, generating, completed, failed
    error_message = Column(Text)
    
    # AI generation metadata
    generation_duration = Column(Integer)  # in seconds
    api_cost = Column(Integer)  # in cents
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    blog_post = relationship("BlogPost", back_populates="assets")
    
    def __repr__(self):
        return f"<Asset(id={self.id}, type='{self.asset_type}', blog_post_id={self.blog_post_id})>"

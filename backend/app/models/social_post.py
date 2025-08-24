from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class SocialPost(Base):
    __tablename__ = "social_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    blog_post_id = Column(Integer, ForeignKey("blog_posts.id"), nullable=False)
    
    # Platform-specific content
    platform = Column(String(50), nullable=False)  # twitter, instagram, linkedin, etc.
    content = Column(Text, nullable=False)
    
    # Social media specific fields
    hashtags = Column(JSON, default=list)  # List of hashtags
    mentions = Column(JSON, default=list)  # List of @mentions
    call_to_action = Column(Text)
    
    # Character counts and limits
    character_count = Column(Integer)
    is_within_limits = Column(Boolean, default=True)
    
    # AI generation metadata
    prompt_used = Column(Text)
    model_used = Column(String(100))
    tokens_used = Column(Integer)
    
    # User interaction
    is_approved = Column(Boolean, default=False)
    user_notes = Column(Text)
    
    # Status
    status = Column(String(50), default="draft")  # draft, approved, scheduled, published
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    blog_post = relationship("BlogPost", back_populates="social_posts")
    
    def __repr__(self):
        return f"<SocialPost(id={self.id}, platform='{self.platform}', blog_post_id={self.blog_post_id})>"

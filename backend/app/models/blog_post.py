from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class BlogPost(Base):
    __tablename__ = "blog_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    idea_id = Column(Integer, ForeignKey("ideas.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    persona_id = Column(Integer, ForeignKey("personas.id"), nullable=False)
    
    # Content
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True)
    content = Column(Text, nullable=False)
    excerpt = Column(Text)
    
    # Metadata
    word_count = Column(Integer)
    reading_time = Column(Integer)  # in minutes
    category = Column(String(100))
    tags = Column(JSON, default=list)
    
    # SEO
    meta_title = Column(String(255))
    meta_description = Column(Text)
    
    # User interaction
    is_approved = Column(Boolean, default=False)
    user_notes = Column(Text)
    user_edits = Column(JSON, default=list)  # Track edit history
    
    # AI generation metadata
    model_used = Column(String(100))
    tokens_used = Column(Integer)
    generation_duration = Column(Integer)  # in seconds
    
    # Status
    status = Column(String(50), default="draft")  # draft, approved, generating_assets, completed
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    idea = relationship("Idea", back_populates="blog_post")
    user = relationship("User", back_populates="blog_posts")
    persona = relationship("Persona")
    assets = relationship("Asset", back_populates="blog_post", cascade="all, delete-orphan")
    social_posts = relationship("SocialPost", back_populates="blog_post", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<BlogPost(id={self.id}, title='{self.title}', idea_id={self.idea_id})>"

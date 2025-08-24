from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Idea(Base):
    __tablename__ = "ideas"
    
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Idea content
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    angle = Column(Text)  # The unique "take" on the topic
    current_event_hook = Column(Text)  # How it ties to current events
    
    # AI generation metadata
    prompt_used = Column(Text)
    model_used = Column(String(100))
    tokens_used = Column(Integer)
    
    # User interaction
    is_approved = Column(Boolean, default=False)
    is_rejected = Column(Boolean, default=False)
    user_notes = Column(Text)
    
    # Status tracking
    status = Column(String(50), default="generated")  # generated, approved, rejected, researching, writing
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    topic = relationship("Topic", back_populates="ideas")
    user = relationship("User", back_populates="ideas")
    research = relationship("Research", back_populates="idea", uselist=False, cascade="all, delete-orphan")
    blog_post = relationship("BlogPost", back_populates="idea", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Idea(id={self.id}, title='{self.title}', topic_id={self.topic_id})>"

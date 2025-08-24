from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Topic metadata
    category = Column(String(100))  # technology, business, politics, etc.
    keywords = Column(JSON, default=list)  # list of keywords
    target_audience = Column(String(100))
    
    # Generation settings
    idea_count = Column(Integer, default=10)
    target_word_count = Column(Integer, default=1000)
    persona_id = Column(Integer, ForeignKey("personas.id"))
    
    # Status tracking
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="topics")
    ideas = relationship("Idea", back_populates="topic", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Topic(id={self.id}, title='{self.title}', user_id={self.user_id})>"

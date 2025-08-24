from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Research(Base):
    __tablename__ = "research"
    
    id = Column(Integer, primary_key=True, index=True)
    idea_id = Column(Integer, ForeignKey("ideas.id"), nullable=False)
    
    # Research prompt
    research_prompt = Column(Text, nullable=False)
    
    # Research findings
    key_findings = Column(JSON, default=list)  # List of key insights
    outline = Column(JSON, default=dict)  # Generated outline structure
    
    # Sources and citations
    sources = Column(JSON, default=list)  # List of source objects with URL, title, etc.
    source_count = Column(Integer, default=0)
    
    # AI generation metadata
    model_used = Column(String(100))
    tokens_used = Column(Integer)
    research_duration = Column(Integer)  # in seconds
    
    # Status
    status = Column(String(50), default="pending")  # pending, researching, completed, failed
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    idea = relationship("Idea", back_populates="research")
    
    def __repr__(self):
        return f"<Research(id={self.id}, idea_id={self.idea_id}, status='{self.status}')>"

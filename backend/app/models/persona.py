from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Persona(Base):
    __tablename__ = "personas"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Writing style preferences
    writing_style = Column(String(50), default="professional")  # professional, casual, technical, conversational
    tone = Column(String(50), default="neutral")  # neutral, authoritative, friendly, challenging
    target_audience = Column(String(100), default="general")
    
    # Content preferences
    include_statistics = Column(Boolean, default=True)
    include_examples = Column(Boolean, default=True)
    include_case_studies = Column(Boolean, default=False)
    include_quotes = Column(Boolean, default=False)
    
    # Structure preferences
    always_key_takeaways = Column(Boolean, default=True)
    include_call_to_action = Column(Boolean, default=False)
    preferred_section_count = Column(Integer, default=5)
    
    # Custom preferences as JSON
    custom_preferences = Column(JSON, default=dict)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="personas")
    
    def __repr__(self):
        return f"<Persona(id={self.id}, name='{self.name}', user_id={self.user_id})>"

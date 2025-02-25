from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from .base import Base

class Messages(Base):
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, nullable=False)
    sender = Column(String, nullable=False)
    created_at = Column(DateTime)
    edited_at = Column(DateTime)
    intent_id = Column(Integer, ForeignKey("intents.intent_id"))
    response_id = Column(Integer, ForeignKey("responses.response_id"))
    project_id = Column(Integer, ForeignKey("projects.project_id"))
    suggested_team_json = Column(String)
    

    # Relationships
    user = relationship("User", back_populates="messages")
    project = relationship("Project", back_populates="messages")
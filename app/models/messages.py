from sqlalchemy import Column, Integer, String, Boolean, DateTime, ARRAY, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import Base

class Messages(Base):
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("chat.conversation_id"), nullable=False)
    sender = Column(String)
    message_text = Column(String)
    created_at = Column(DateTime)
    edited_at = Column(DateTime)
    intent_id = Column(Integer, ForeignKey("intents.intent_id"))
    response_id = Column(Integer, ForeignKey("responses.response_id"))
    project_id = Column(Integer, ForeignKey("projects.project_id"))
    suggested_team_json = Column(JSON, comment='Structured JSON data containing AI suggested team composition')

    # Relationship
    chats = relationship("Chat", back_populates="messages")
    intent = relationship("Intent", back_populates="messages")
    response = relationship("Response", back_populates="messages")
    projects = relationship("Project", back_populates="messages")
    feedback = relationship("Feedback", back_populates="message")

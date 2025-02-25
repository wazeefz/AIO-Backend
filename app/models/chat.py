from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Chat(Base):
    __tablename__ = "chat"

    conversation_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    started_at = Column(DateTime(timezone=True))
    ended_at = Column(DateTime(timezone=True))
    project_id = Column(Integer, ForeignKey("projects.project_id"))

    # Relationships (Bi-directional)
    user = relationship("User", back_populates="chats")  # Relationship to User
    project = relationship("Project", back_populates="chats") # Relationship to Project
    messages = relationship("Messages", back_populates="chats")
from sqlalchemy import Column, Integer, String , DateTime
from sqlalchemy.orm import relationship
from .base import Base

class Feedback(Base):
    __tablename__ = "feedback"

    feedback_id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)
    feedback_text = Column(String, nullable=False)

    # Relationships
    users = relationship("User", back_populates="feedback")
    talents = relationship("Talent", back_populates="feedback")

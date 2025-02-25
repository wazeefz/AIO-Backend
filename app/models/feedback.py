from sqlalchemy import Column, Integer, String, Boolean, DateTime, ARRAY, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Feedback(Base):
    __tablename__ = "feedback"

    feedback_id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.message_id"))
    rating = Column(Integer)
    created_at = Column(DateTime)
    feedback_text = Column(String)

    # Relationships
    message = relationship("Messages", back_populates="feedback")
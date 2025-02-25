from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from .base import Base

class Responses(Base):
    __tablename__ = "responses"

    response_id = Column(Integer, primary_key=True, index=True)
    intent_id = Column(Integer, ForeignKey("intents.intent_id"))
    response_text = Column(String, nullable=False)
    response_template = Column(String)

    # Relationships
    user = relationship("User", back_populates="responses")
    project = relationship("Project", back_populates="responses")
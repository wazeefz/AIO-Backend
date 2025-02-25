from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from .base import Base

class Intent(Base):
    __tablename__ = "intents"

    intent_id = Column(Integer, primary_key=True, index=True)
    intent_name = Column(String, nullable=False)
    description = Column(Text)

    # Relationship to the Message model (bi-directional)
    messages = relationship("Messages", back_populates="intent")
    responses = relationship("Response", back_populates="intent")
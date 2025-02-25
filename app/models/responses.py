from sqlalchemy import Column, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import Base

class Response(Base):
    __tablename__ = "responses"

    response_id = Column(Integer, primary_key=True, index=True)
    intent_id = Column(Integer, ForeignKey("intents.intent_id"))
    response_text = Column(Text)
    response_template = Column(JSON)

    # Relationships (Bi-directional)
    intent = relationship("Intent", back_populates="responses")
    messages = relationship("Messages", back_populates="response")
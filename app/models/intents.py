from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from .base import Base

class Intent(Base):
    __tablename__ = "intents"

    intent_id = Column(Integer, primary_key=True, index=True)
    intent_name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    project_id = Column(Integer, ForeignKey("projects.project_id"))


    # Relationships
    users = relationship("User", back_populates="intents")
    projects = relationship("Project", back_populates="intents")
    
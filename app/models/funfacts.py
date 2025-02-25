from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from .base import Base

class FunFact(Base):
    __tablename__ = "funfacts"

    fun_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"))
    talent_id = Column(Integer, ForeignKey("talents.talent_id"))
    fun_text = Column(String, nullable=False)
    fact_type = Column(String, nullable=False)
    relevance_score = Column(Integer, nullable=False)

    # Relationships
    users = relationship("User", back_populates="feedback")
    talents = relationship("Talent", back_populates="feedback")
    projects = relationship("Project", back_populates="feedback")

from sqlalchemy import Column, Integer, String, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from .base import Base  

class FunFacts(Base):
    __tablename__ = "funfacts"

    fun_id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # SERIAL in PostgreSQL becomes autoincrement=True
    project_id = Column(Integer, ForeignKey("projects.project_id", ondelete="CASCADE"))
    talent_id = Column(Integer, ForeignKey("talents.talent_id", ondelete="CASCADE"))
    fun_text = Column(String(100))
    fact_type = Column(String(50))
    relevance_score = Column(Numeric(3, 2))  # For DECIMAL(3,2)

    # Define relationships (optional but helpful)
    project = relationship("Project", back_populates="fun_facts")
    talent = relationship("Talent", back_populates="fun_facts")
    
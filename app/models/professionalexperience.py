from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from .base import Base

class ProfessionalExperience(Base):
    __tablename__ = "professional_experience"
    
    experience_id = Column(Integer, primary_key=True, index=True)
    talent_id = Column(Integer, ForeignKey("talents.talent_id"))
    company = Column(String, nullable=False)
    job_title = Column(String, nullable=False)
    location = Column(String)
    employment_type = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    is_current_job = Column(Boolean, default=False)
    description = Column(String)
    achievements = Column(ARRAY(String))
    
    # Relationships
    user = relationship("User", back_populates="professional_experience")
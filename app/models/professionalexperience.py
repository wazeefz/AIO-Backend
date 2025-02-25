from sqlalchemy import Column, Integer, String, Boolean, DateTime, ARRAY, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class ProfessionalExperience(Base):
    __tablename__ = "professionalexperience"

    experience_id = Column(Integer, primary_key=True, index=True)
    talent_id = Column(Integer, ForeignKey("talents.talent_id"))
    company_name = Column(String)
    job_title = Column(String)
    location = Column(String)
    employment_type = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    is_current_job = Column(Boolean)
    description = Column(String)
    key_achievements = Column(ARRAY(String))

    # Relationships
    talent = relationship("Talent", back_populates="professional_experience")
    skills = relationship("ExperienceSkills", back_populates="experience")

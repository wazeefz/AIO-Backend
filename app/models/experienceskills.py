from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base  

class ExperienceSkills(Base):
    __tablename__ = "experienceskills"

    experience_id = Column(Integer, ForeignKey("professionalexperience.experience_id", ondelete="CASCADE"), primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.skill_id", ondelete="CASCADE"), primary_key=True)

    # Define relationships (optional but helpful)
    experience = relationship("ProfessionalExperience", back_populates="skills") 
    skill = relationship("Skill", back_populates="experienceskills") 

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Skill(Base):
    __tablename__ = "skills"

    skill_id = Column(Integer, primary_key=True, index=True)
    skill_name = Column(String, nullable=False)
    skill_category = Column(String, nullable=False)

    # Relationships
    talent_skills = relationship("TalentSkill", back_populates="skill", cascade="all, delete")
    experienceskills = relationship("ExperienceSkills", back_populates="skill")
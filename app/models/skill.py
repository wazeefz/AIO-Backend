from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Skill(Base):
    __tablename__ = "skills"

    skill_id = Column(Integer, primary_key=True, index=True)
    skill_name = Column(String, unique=True)
    # skill_category = Column(String)

    # Relationships
    talent_skills = relationship("TalentSkill", back_populates="skill", cascade="all, delete-orphan")
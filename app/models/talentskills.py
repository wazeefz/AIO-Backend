from sqlalchemy import Column, Integer, DateTime, ForeignKey, Float, Numeric
from sqlalchemy.orm import relationship
from .base import Base

class TalentSkill(Base):
    __tablename__ = "talentskills"

    talent_id = Column(Integer, ForeignKey("talents.talent_id"), primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.skill_id"), primary_key=True)
    proficiency_level = Column(Integer)
    years_of_experience = Column(Numeric(4, 2))
    last_used_date = Column(DateTime)

    # Relationships
    talent = relationship("Talent", back_populates="talent_skills")
    skill = relationship("Skill", back_populates="talent_skills")

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class TalentSkill(Base):
    __tablename__ = "talentskills"

    # Composite primary key using talent_id and skill_id
    talent_id = Column(Integer, ForeignKey("talents.talent_id", ondelete="CASCADE"), primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.skill_id", ondelete="CASCADE"), primary_key=True)
    proficiency_level = Column(Integer)  # Changed to Integer as per DB structure

    # Relationships
    talent = relationship("Talent", back_populates="talent_skills")
    skill = relationship("Skill", back_populates="talent_skills")

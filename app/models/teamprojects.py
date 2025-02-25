from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from .base import Base

class TeamProjects(Base):
    __tablename__ = "teamprojects"

    project_id = Column(Integer, primary_key=True, index=True)
    talent_id = Column(Integer, ForeignKey("talents.talent_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))

    # Relationships
    talent = relationship("Talent", back_populates="teamprojects")
    user = relationship("User", back_populates="teamprojects")
    projects = relationship("Project", back_populates="teamprojects")
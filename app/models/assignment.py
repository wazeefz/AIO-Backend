from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class ProjectAssignment(Base):
    __tablename__ = "projectassignments"

    assignment_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"))
    talent_id = Column(Integer, ForeignKey("talents.talent_id"))
    role = Column(String)
    assignment_start_date = Column(DateTime)
    assignment_end_date = Column(DateTime)
    # performance_rating = Column(Integer)
    tech_skill = Column(Integer, nullable=False)
    quality = Column(Integer, nullable=False)
    collaboration = Column(Integer, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="project_assignments")
    talent = relationship("Talent", back_populates="project_assignments")

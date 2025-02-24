from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class ProjectAssignments(Base):
    __tablename__ = "projectassignments"

    assignment_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"))
    talent_id = Column(Integer, ForeignKey("talents.talent_id"))
    role = Column(String(50))
    assignment_start_date = Column(Date)
    assignment_end_date = Column(Date)
    performance_rating = Column(Integer)

    # Relationships
    project = relationship("Project", back_populates="assignments")
    talent = relationship("Talent", back_populates="assignments")

from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from .base import Base

class ProjectAssignment(Base):
    __tablename__ = "projectsassignment"

    assignment_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"))
    talent_id = Column(Integer, ForeignKey("talents.talent_id"))
    role = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    rating = Column(Integer)

    # Relationships
    project = relationship("Project", back_populates="projectsassignment")
    user = relationship("User", back_populates="projectsassignment")
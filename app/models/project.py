from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from .base import Base

class Project(Base):
    __tablename__ = "projects"

    project_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    starred = Column(Boolean, default=False)
    cv_count = Column(Integer, default=0)
    progress = Column(Integer)
    status = Column(String)
    budget = Column(Float)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    start_date = Column(DateTime)
    required_skills = Column(ARRAY(Integer))
    min_experience_years = Column(Integer)
    team_size = Column(Integer)
    project_description = Column(String)

    # Added new fields
    project_period = Column(String(50))
    tech_skill = Column(Integer, nullable=False)
    quality = Column(Integer, nullable=False)
    collaboration = Column(Integer, nullable=False)
    remarks = Column(String)


    # Relationships
    user = relationship("User", back_populates="projects")
    project_assignments = relationship("ProjectAssignment", back_populates="project")

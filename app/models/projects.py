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
    due_date = Column(DateTime)
    status = Column(String)
    budget = Column(Float)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    start_date = Column(DateTime)
    created_at = Column(DateTime)
    required_skills = Column(ARRAY(Integer))
    min_experience_years = Column(Integer)
    team_size = Column(Integer)
    project_description = Column(String)

    # Relationships
    user = relationship("User", back_populates="projects")
    project_assignments = relationship("ProjectAssignment", back_populates="project")
    team_members = relationship("TeamProjects", back_populates="project")
    fun_facts = relationship("FunFacts", back_populates="project")
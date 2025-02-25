from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base  

class TeamProjects(Base):
    __tablename__ = "teamprojects"

    project_id = Column(Integer, ForeignKey("projects.project_id", ondelete="CASCADE"), primary_key=True)
    talent_id = Column(Integer, ForeignKey("talents.talent_id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)

    # Define relationships (optional but helpful)
    project = relationship("Project", back_populates="team_members")
    talent = relationship("Talent", back_populates="project_teams")
    user = relationship("User", back_populates="project_teams")

    
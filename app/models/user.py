from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(String)
    department_id = Column(Integer, ForeignKey("department.department_id"))
    feedback_id = Column(Integer, ForeignKey("feedback.feedback_id"))
    intent_id = Column(Integer, ForeignKey("intents.intent_id"))
    fun_id = Column(Integer, ForeignKey("funfacts.fun_id"))
    # project_id = Column(Integer, ForeignKey("projects.project_id"))


    # Relationships
    department = relationship("Department", back_populates="users")
    projects = relationship("Project", back_populates="user")
    feedback = relationship("Feedback", back_populates="users")

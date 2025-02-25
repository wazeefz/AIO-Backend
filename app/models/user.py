from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey("department.department_id"))
    email = Column(String, unique=True, nullable=False)
    role = Column(String)

    # Relationships
    department = relationship("Department", back_populates="users")
    projects = relationship("Project", back_populates="user")
    chats = relationship("Chat", back_populates="user")

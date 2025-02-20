from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base

class Department(Base):
    __tablename__ = "department"

    department_id = Column(Integer, primary_key=True, index=True)
    department_name = Column(String, nullable=False)

    # Relationships
    users = relationship("User", back_populates="department")
    talents = relationship("Talent", back_populates="department")

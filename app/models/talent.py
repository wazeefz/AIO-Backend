from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Talent(Base):
    __tablename__ = "talents"

    talent_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)
    job_title = Column(String)
    employment_type = Column(String)
    department_id = Column(Integer, ForeignKey("department.department_id"))
    hire_date = Column(DateTime)
    basic_salary = Column(Float, nullable=False, default=0)
    gender = Column(String)
    date_of_birth = Column(DateTime)
    marital_status = Column(Boolean)
    total_experience_years = Column(Float, nullable=False, default=0.0)
    career_preferences = Column(String)
    availability_status = Column(String, nullable=False, default="available")


    # Relationships
    department = relationship("Department", back_populates="talents")
    talent_skills = relationship("TalentSkill", back_populates="talent", cascade="all, delete-orphan")
    education = relationship("Education", back_populates="talent", cascade="all, delete")
    professional_experience = relationship("ProfessionalExperience", back_populates="talent", cascade="all, delete")
    project_assignments = relationship("ProjectAssignment", back_populates="talent", cascade="all, delete")

    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            "talent_id": self.talent_id,
            "name": f"{self.first_name} {self.last_name}",
            "first_name": self.first_name,
            "last_name": self.last_name,
            "department_id": self.department_id
        }

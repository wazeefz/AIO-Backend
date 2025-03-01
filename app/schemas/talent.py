from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Base Schema - Shared attributes
class TalentBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    job_title: Optional[str] = None
    employment_type: Optional[str] = None
    department_id: Optional[int] = None
    hire_date: Optional[datetime] = None
    basic_salary: Optional[float] = None
    gender: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    marital_status: Optional[bool] = None
    total_experience_years: Optional[float] = None
    career_preferences: Optional[str] = None
    availability_status: Optional[str] = None

    # Added new fields
    age: int
    current_country: str
    current_city: str
    willing_to_relocate: bool
    professional_summary: Optional[str] = None
    position_level: str
    tech_skill: int
    soft_skill: int
    interview_remarks: Optional[str] = None

# Response Schema - Includes ID (read-only)
class TalentResponse(TalentBase):
    talent_id: int

    class Config:
        from_attributes = True  # Ensures compatibility with ORM models

class TalentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    employment_type: Optional[str] = None
    department_id: Optional[int] = None
    hire_date: Optional[datetime] = None
    basic_salary: Optional[float] = None
    gender: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    marital_status: Optional[bool] = None
    total_experience_years: Optional[float] = None
    career_preferences: Optional[str] = None
    availability_status: Optional[str] = None

    # Added new fields
    age: Optional[int] = None
    current_country: Optional[str] = None
    current_city: Optional[str] = None
    willing_to_relocate: Optional[bool] = None
    professional_summary: Optional[str] = None
    position_level: Optional[str] = None
    tech_skill: Optional[int] = None
    soft_skill: Optional[int] = None
    interview_remarks: Optional[str] = None

    class Config:
        from_attributes = True  # Ensures compatibility with ORM models

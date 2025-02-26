from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

# Base Schema with shared config
class ProjectAssignmentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # Updated for Pydantic v2
    project_id: int
    talent_id: int
    role: Optional[str] = None
    assignment_start_date: Optional[datetime] = None
    assignment_end_date: Optional[datetime] = None
    performance_rating: Optional[float] = None

# Create Schema - Used for creating new assignments
class ProjectAssignmentCreate(ProjectAssignmentBase):
    project_id: int  # Required field
    talent_id: int   # Required field

# Update Schema - All fields optional for updates
class ProjectAssignmentUpdate(BaseModel):
    role: Optional[str] = None
    assignment_start_date: Optional[datetime] = None
    assignment_end_date: Optional[datetime] = None
    performance_rating: Optional[float] = None

# Response Schema - Includes ID and relationships
class ProjectAssignmentResponse(ProjectAssignmentBase):
    assignment_id: int

    class Config:
        from_attributes = True  # Ensures compatibility with ORM models

# Update the AvailableTalentResponse schema
class AvailableTalentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    talent_id: int
    first_name: str
    last_name: str
    email: str
    basic_salary: float 
    phone: Optional[str] = None
    job_title: Optional[str] = None
    department_name: Optional[str] = None
    total_experience_years: Optional[float] = None

class ProjectTeamMemberResponse(BaseModel):
    talent_id: int
    first_name: str
    last_name: str
    job_title: str
    basic_salary: float 
    role: Optional[str]
    email: str
    department_name: Optional[str] = None
    performance_rating: Optional[float]
    assignment_start_date: Optional[datetime]
    assignment_end_date: Optional[datetime]
    total_experience_years: Optional[float] = None

    class Config:
        from_attributes = True
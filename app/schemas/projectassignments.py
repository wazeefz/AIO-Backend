from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date, datetime

# Base Schema with shared config
class ProjectAssignmentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # Updated for Pydantic v2
    project_id: int
    talent_id: int
    role: Optional[str] = None
    assignment_start_date: Optional[date] = None
    assignment_end_date: Optional[date] = None
    performance_rating: Optional[int] = None

# Create Schema - Used for creating new assignments
class ProjectAssignmentCreate(ProjectAssignmentBase):
    project_id: int  # Required field
    talent_id: int   # Required field

# Update Schema - All fields optional for updates
class ProjectAssignmentUpdate(BaseModel):
    role: Optional[str] = None
    assignment_start_date: Optional[date] = None
    assignment_end_date: Optional[date] = None
    performance_rating: Optional[int] = None

# Response Schema - Includes ID and relationships
class ProjectAssignmentResponse(ProjectAssignmentBase):
    assignment_id: int

    class Config:
        from_attributes = True  # Ensures compatibility with ORM models

# Optional: Extended Response Schema with nested project and talent details
class ProjectAssignmentExtendedResponse(ProjectAssignmentResponse):
    project_name: Optional[str] = None
    talent_first_name: Optional[str] = None
    talent_last_name: Optional[str] = None
    talent_job_title: Optional[str] = None

    class Config:
        from_attributes = True

# Update the AvailableTalentResponse schema
class AvailableTalentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    talent_id: int
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    job_title: Optional[str] = None
    employment_type: Optional[str] = None
    department_id: Optional[int] = None
    hire_date: Optional[datetime] = None
    availability_status: Optional[str] = None
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date, datetime

# Base Schema with shared config
class ProjectAssignmentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # Updated for Pydantic v2
    project_id: int
    talent_id: int
    role: Optional[str] = None
    assignment_start_date: Optional[datetime] = None
    assignment_end_date: Optional[datetime] = None
    # performance_rating: Optional[float] = None
    tech_skill: Optional[int] = None
    quality: Optional[int] = None
    collaboration: Optional[int] = None

# Create Schema - Used for creating new assignments
class ProjectAssignmentCreate(ProjectAssignmentBase):
    project_id: int  # Required field
    talent_id: int   # Required field

# Update Schema - All fields optional for updates
class ProjectAssignmentUpdate(BaseModel):
    role: Optional[str] = None
    assignment_start_date: Optional[datetime] = None
    assignment_end_date: Optional[datetime] = None
    # performance_rating: Optional[float] = None
    tech_skill: Optional[int] = None
    quality: Optional[int] = None
    collaboration: Optional[int] = None

# Response Schema - Includes ID and relationships
class ProjectAssignmentResponse(ProjectAssignmentBase):
    assignment_id: int

    class Config:
        from_attributes = True  # Ensures compatibility with ORM models

# Optional: Extended Response Schema with nested project and talent details
class ProjectAssignmentExtendedResponse(ProjectAssignmentResponse):
    # Project details
    project_name: Optional[str] = None
    project_status: Optional[str] = None
    project_progress: Optional[float] = None
    project_budget: Optional[float] = None
    project_start_date: Optional[datetime] = None
    project_description: Optional[str] = None
    
    # Talent details
    talent_first_name: Optional[str] = None
    talent_last_name: Optional[str] = None
    talent_email: Optional[str] = None
    talent_phone: Optional[str] = None
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
    department_name: Optional[str] = None

class ProjectTeamMemberResponse(BaseModel):
    talent_id: int
    first_name: str
    last_name: str
    job_title: str
    role: Optional[str]
    email: str
    # performance_rating: Optional[float]
    tech_skill: Optional[int]
    quality: Optional[int]
    collaboration: Optional[int]
    assignment_start_date: Optional[datetime]
    assignment_end_date: Optional[datetime]

    class Config:
        from_attributes = True
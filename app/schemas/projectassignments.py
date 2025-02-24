from pydantic import BaseModel
from typing import Optional
from datetime import date

# Base Schema - Shared attributes
class ProjectAssignmentBase(BaseModel):
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
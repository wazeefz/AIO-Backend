from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Base Schema - Shared attributes
class ProjectAssignmentBase(BaseModel):
    project_id: int
    talent_id: int
    role: str
    start_date: datetime
    end_date: datetime
    rating: int

# Create Schema - Used for input validation when creating a new project assignment
class ProjectAssignmentCreate(ProjectAssignmentBase):
    project_id: int  # Required field
    talent_id: int  # Required field
    role: str  # Required field
    start_date: datetime  # Required field
    end_date: datetime  # Required field
    rating: int  # Required field

# Update Schema - Used when updating an existing project assignment
class ProjectAssignmentUpdate(ProjectAssignmentBase):
    pass  # All fields are optional

# Response Schema - Includes ID (read-only)
class ProjectAssignmentResponse(ProjectAssignmentBase):
    assignment_id: int

    class Config:
        from_attributes = True  # Ensures compatibility with ORM models
        
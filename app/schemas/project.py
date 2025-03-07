from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Base Schema - Shared attributes
class ProjectBase(BaseModel):
    name: str
    project_description: Optional[str] = None
    starred: Optional[bool] = False
    # cv_count: Optional[int] = 0
    progress: Optional[int] = None
    status: Optional[str] = None
    budget: Optional[float] = None
    user_id: Optional[int] = None
    # start_date: Optional[datetime] = None
    # required_skills: Optional[List[int]] = []
    # min_experience_years: Optional[int] = None
    team_size: Optional[int] = None

    # Added new fields
    project_period: Optional[str] = None
    # tech_skill: int
    # quality: int
    # collaboration: int
    remarks: Optional[str] = None

# Create Schema - Used for input validation when creating a new project
class ProjectCreate(ProjectBase):
    name: str  # Required field

# Update Schema - Used when updating an existing project
class ProjectUpdate(ProjectBase):
    pass  # All fields are optional

# Response Schema - Includes ID (read-only)
class ProjectResponse(ProjectBase):
    project_id: int

    class Config:
        from_attributes = True  # Ensures compatibility with ORM models

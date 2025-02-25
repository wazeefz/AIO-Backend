from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Base Schema - Shared attributes
class TeamProjectsBase(BaseModel):
    talent_id: int
    user_id: int
    project: int

# Create Schema - Used for input validation when creating a new teamproject
class TeamProjectsCreate(TeamProjectsBase):
    talent_id: int  # Required field
    user_id: int  # Required field
    project: int  # Required field

# Update Schema - Used when updating an existing teamproject
class TeamProjectsUpdate(TeamProjectsBase):
    pass  # All

# Response Schema - Includes ID (read-only)
class TeamProjectsResponse(TeamProjectsBase):
    project_id: int

    class Config:
        from_attributes = True  # Ensures compatibility with ORM models
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Base Schema - Shared attributes
class ProfessionalExperienceBase(BaseModel):
    company: str
    job_title: str
    location: Optional[str] = None
    employment_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_current_job: Optional[bool] = False
    description: Optional[str] = None
    achievements: Optional[List[str]] = []

# Create Schema - Used for input validation when creating a new professional experience
class ProfessionalExperienceCreate(ProfessionalExperienceBase):
    company: str  # Required field
    job_title: str  # Required field

# Update Schema - Used when updating an existing professional experience
class ProfessionalExperienceUpdate(ProfessionalExperienceBase):
    pass  # All fields are optional

# Response Schema - Includes ID (read-only)
class ProfessionalExperienceResponse(ProfessionalExperienceBase):
    experience_id: int

    class Config:
        from_attributes = True  # Ensures compatibility with ORM models
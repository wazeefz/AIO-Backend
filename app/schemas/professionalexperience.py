from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProfessionalExperienceBase(BaseModel):
    company_name: str
    job_title: str
    location: Optional[str] = None
    employment_type: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    is_current_job: bool
    description: Optional[str] = None
    key_achievements: Optional[List[str]] = None

class ProfessionalExperienceResponse(ProfessionalExperienceBase):
    experience_id: int
    talent_id: int

    class Config:
        from_attributes = True  # Ensures compatibility with ORM models

class ProfessionalExperienceCreate(ProfessionalExperienceBase):
    talent_id: int

class ProfessionalExperienceUpdate(BaseModel):
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_current_job: Optional[bool] = None
    description: Optional[str] = None
    key_achievements: Optional[List[str]] = None

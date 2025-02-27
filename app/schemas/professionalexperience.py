from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProfessionalExperienceBase(BaseModel):
    company_name: str
    experience_id: int
    job_title: str
    location: str
    employment_type: str
    start_date: datetime
    end_date: datetime | None = None  # Optional end date
    is_current_job: bool
    description: str
    key_achievements: List[str]


class ProfessionalExperienceCreate(ProfessionalExperienceBase):
    talent_id: int  # Include talent_id for creation


class ProfessionalExperienceResponse(ProfessionalExperienceBase):
    experience_id: int
    talent_id: int

    class Config:
        from_attributes = True  # Important for converting SQLAlchemy objects to Pydantic models

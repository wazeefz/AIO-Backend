from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

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
    skills: List[str] = []

class ProjectTeamMemberResponse(BaseModel):
    talent_id: int
    first_name: str
    last_name: str
    job_title: str
    basic_salary: float 
    role: Optional[str]
    email: str
    department_name: Optional[str] = None
    # performance_rating: Optional[float]
    assignment_start_date: Optional[datetime]
    assignment_end_date: Optional[datetime]
    total_experience_years: Optional[float] = None
    skills: List[str] = []

    class Config:
        from_attributes = True
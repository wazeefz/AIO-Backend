from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EducationBase(BaseModel):
    institution_name: str
    qualification_type: str
    field_of_study: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None

class EducationResponse(EducationBase):
    education_id: int
    talent_id: int

    class Config:
        from_attributes = True  # Ensures compatibility with ORM models

class EducationCreate(EducationBase):
    talent_id: int

class EducationUpdate(BaseModel):
    institution_name: Optional[str] = None
    qualification_type: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

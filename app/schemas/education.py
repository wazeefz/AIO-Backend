from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EducationBase(BaseModel):
    talent_id: int
    institution_name: str
    qualification_type: str
    field_of_study: str
    start_date: datetime
    end_date: Optional[datetime] = None

class EducationCreate(EducationBase):
    pass

class EducationUpdate(BaseModel):
    institution_name: Optional[str] = None
    qualification_type: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class EducationResponse(EducationBase):
    education_id: int

    class Config:
        from_attributes = True

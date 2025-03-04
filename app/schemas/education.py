from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class EducationBase(BaseModel):
    talent_id: int
    institution_name: str
    qualification_type: str
    field_of_study: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    @validator('start_date', 'end_date', pre=True)
    def validate_dates(cls, value):
        if value == "" or value is None:
            return None
        return value

class EducationCreate(EducationBase):
    pass

class EducationUpdate(BaseModel):
    talent_id: Optional[int] = None
    institution_name: Optional[str] = None
    qualification_type: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    @validator('start_date', 'end_date', pre=True)
    def validate_dates(cls, value):
        if value == "" or value is None:
            return None
        return value

class EducationResponse(EducationBase):
    education_id: int

    class Config:
        from_attributes = True

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class EducationBase(BaseModel):
    talent_id: int
    institution_name: str
    qualification_type: str
    field_of_study: str
    start_date: datetime
    end_date: datetime

class EducationCreate(EducationBase):
    talent_id: int

class EducationUpdate(EducationBase):
    pass  # All fields optional for updates

class EducationResponse(EducationBase):  # Response schema
    education_id: int

    class Config:
        from_attributes = True

# class EducationList(BaseModel):  # For returning lists of Education
#     educations: List[Education]
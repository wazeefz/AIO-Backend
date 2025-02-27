from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class IntentsBase(BaseModel):
    intent_id: int
    intent_name: str
    description: str

class IntentsCreate(IntentsBase):
    intent_id: int

class IntentsUpdate(IntentsBase):
    pass  # All fields optional for updates

class IntentsResponse(IntentsBase):  # Response schema
    intent_id: int

    class Config:
        from_attributes = True
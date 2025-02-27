from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TeamProjectBase(BaseModel):
    project_id: int
    talent_id: int
    user_id: int
    

class TeamProjectCreate(TeamProjectBase):
    project_id: int

class TeamProjectUpdate(TeamProjectBase):
    pass  # All fields optional for updates

class TeamProjectResponse(TeamProjectBase):  # Response schema
    talent_id: int

    class Config:
        from_attributes = True


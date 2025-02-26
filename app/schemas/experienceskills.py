from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Base Schema - Shared attributes
class ExperienceSkillBase(BaseModel):
    experience_id: int
    skill_id: int

# Create Schema - Used for input validation when creating a new chat
class ExperienceSkillCreate(ExperienceSkillBase):
    experience_id: int

# Update Schema - Used when updating an existing chat
class ExperienceSkillUpdate(ExperienceSkillBase):
    pass


class ExperienceSkillResponse(ExperienceSkillBase):
    skill_id: int

    class Config:
        from_attributes = True

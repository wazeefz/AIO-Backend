from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from .skill import SkillResponse  # Import SkillResponse schema

# Base Schema - Shared attributes
class TalentSkillBase(BaseModel):
    talent_id: int
    skill_id: int
    proficiency_level: int
    years_of_experience: float
    last_used_date: datetime

# Schema for Creating a TalentSkill
class TalentSkillCreate(TalentSkillBase):
    pass

# Schema for Updating a TalentSkill (fields optional)
class TalentSkillUpdate(BaseModel):
    proficiency_level: Optional[int] = None
    years_of_experience: Optional[float] = None
    last_used_date: Optional[datetime] = None

# Response Schema with Skill Details
class TalentSkillResponse(BaseModel):
    proficiency_level: int
    years_of_experience: float
    last_used_date: datetime
    skill: SkillResponse  # ✅ Include skill details

    model_config = ConfigDict(from_attributes=True)  # Pydantic v2 compatibility

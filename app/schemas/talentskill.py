from pydantic import BaseModel, ConfigDict
from typing import Optional

# Base Schema - Shared attributes
class TalentSkillBase(BaseModel):
    talent_id: int
    skill_id: int
    proficiency_level: int

# Schema for Creating a TalentSkill
class TalentSkillCreate(TalentSkillBase):
    pass

# Schema for Updating a TalentSkill (fields optional)
class TalentSkillUpdate(BaseModel):
    proficiency_level: Optional[int] = None

# Response Schema
class TalentSkillResponse(TalentSkillBase):
    model_config = ConfigDict(from_attributes=True)  # Pydantic v2 compatibility

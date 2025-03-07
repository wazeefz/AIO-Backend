from pydantic import BaseModel, ConfigDict
from typing import Optional

# Base Schema - Shared attributes
class SkillBase(BaseModel):
    skill_name: str
    # skill_category: str

# Schema for Creating a Skill
class SkillCreate(SkillBase):
    pass  # Inherits from SkillBase, no changes needed

# Schema for Updating a Skill (fields optional)
class SkillUpdate(BaseModel):
    skill_name: Optional[str] = None
    # skill_category: Optional[str] = None

# Response Schema - Includes ID (read-only)
class SkillResponse(SkillBase):
    skill_id: int

    model_config = ConfigDict(from_attributes=True)  # Pydantic v2 compatibility
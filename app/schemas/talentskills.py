# from pydantic import BaseModel, ConfigDict
# from typing import Optional, List
# from datetime import datetime

# class TalentSkillBase(BaseModel):
#     talent_id: int
#     skill_id: int
#     profieciency_level: int
#     years_of_study: float
#     last_used_date: datetime

# class TalentSkillCreate(TalentSkillBase):
#     pass

# class TalentSkillUpdate(TalentSkillBase):
#     proficiency_level: Optional[int] = None
#     years_of_experience: Optional[float] = None
#     last_used_date: Optional[datetime] = None

# class TalentSkillResponse(TalentSkillBase):  # Response schema
#     model_config = ConfigDict(from_attributes=True)

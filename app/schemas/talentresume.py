from pydantic import BaseModel
from typing import List
from ..schemas.talent import TalentBase
from ..schemas.certification import CertificationCreate, CertificationResponse
from ..schemas.professionalexperience import ProfessionalExperienceCreate, ProfessionalExperienceResponse
from ..schemas.education import EducationCreate, EducationResponse
from ..schemas.talentskill import TalentSkillCreate, TalentSkillResponse

# Schema for Creating a Talent Resume (POST)
class TalentResumeCreate(TalentBase):
    skills: List[TalentSkillCreate] = []
    education: List[EducationCreate] = []
    professional_experience: List[ProfessionalExperienceCreate] = []
    certifications: List[CertificationCreate] = []

    class Config:
        from_attributes = True

# Schema for Retrieving a Talent Resume (GET)
class TalentResumeResponse(TalentBase):
    skills: List[TalentSkillResponse] = []
    education: List[EducationResponse] = []
    professional_experience: List[ProfessionalExperienceResponse] = []
    certifications: List[CertificationResponse] = []

    class Config:
        from_attributes = True

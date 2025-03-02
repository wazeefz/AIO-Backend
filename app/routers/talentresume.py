from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..database import get_db
from ..models import Talent, TalentSkill, Education, ProfessionalExperience, Certification
from ..schemas.talentresume import TalentResumeCreate, TalentResumeResponse

router = APIRouter(prefix="/talent-resume", tags=["talent-resume"])

@router.post("/", response_model=TalentResumeResponse)
def create_talent_resume(resume_data: TalentResumeCreate, db: Session = Depends(get_db)):
    """
    Creates a new talent resume, including skills, education, experiences, and certifications.
    """
    try:
        # Create a new Talent entry
        new_talent = Talent(
            first_name=resume_data.firstName,
            last_name=resume_data.lastName,
            email=resume_data.email,
            phone=resume_data.phone,
            current_city=resume_data.currentCity,
            current_country=resume_data.currentCountry,
            job_title=resume_data.jobTitle,
            professional_summary=resume_data.summary,
            willing_to_relocate=resume_data.willingToRelocate,
            employment_type=resume_data.employmentType,
            total_experience_years=resume_data.experience
        )

        db.add(new_talent)
        db.commit()
        db.refresh(new_talent)

        talent_id = new_talent.talent_id

        # Insert new skills
        skills = [TalentSkill(skill_name=skill, talent_id=talent_id) for skill in resume_data.skills]

        # Insert new education records
        education_records = [Education(**edu.model_dump(), talent_id=talent_id) for edu in resume_data.education]

        # Insert new professional experiences
        professional_experiences = [
            ProfessionalExperience(**exp.model_dump(), talent_id=talent_id) for exp in resume_data.experiences
        ]

        # Insert new certifications
        certifications = [Certification(**cert.model_dump(), talent_id=talent_id) for cert in resume_data.certifications]

        # Add to session & commit
        db.add_all(skills + education_records + professional_experiences + certifications)
        db.commit()

        return TalentResumeResponse(
            talent_id=new_talent.talent_id,
            first_name=new_talent.first_name,
            last_name=new_talent.last_name,
            email=new_talent.email,
            phone=new_talent.phone,
            current_city=new_talent.current_city,
            current_country=new_talent.current_country,
            total_experience_years=new_talent.total_experience_years,
            job_title=new_talent.job_title,
            summary=new_talent.professional_summary,
            willing_to_relocate=new_talent.willing_to_relocate,
            basic_salary=new_talent.basic_salary,
            skills=skills,
            education=education_records,
            professional_experience=professional_experiences,
            certifications=certifications,
        )

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists.")

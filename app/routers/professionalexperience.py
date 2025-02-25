from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.professionalexperience import ProfessionalExperience
from ..schemas.professionalexperience import ProfessionalExperienceBase, ProfessionalExperienceResponse, ProfessionalExperienceCreate, ProfessionalExperienceUpdate

router = APIRouter(prefix="/professionalexperience", tags=["professionalexperience"])

@router.get("/", response_model=List[ProfessionalExperienceResponse])
def get_professionalexperience(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(ProfessionalExperience).offset(skip).limit(limit).all()

@router.get("/{experience_id}", response_model=ProfessionalExperienceResponse)
def get_professionalexperience(experience_id: int, db: Session = Depends(get_db)):
    experience = db.query(ProfessionalExperience).filter(ProfessionalExperience.experience_id == experience_id).first()
    if experience is None:
        raise HTTPException(status_code=404, detail="Professional experience not found")
    return experience

@router.post("/", response_model=ProfessionalExperienceResponse)
def create_professionalexperience(experience: ProfessionalExperienceBase, db: Session = Depends(get_db)):
    if db.query(ProfessionalExperience).filter(ProfessionalExperience.company == experience.company).first():
        raise HTTPException(status_code=400, detail="Professional experience already exists")
    
    new_experience = ProfessionalExperience(**experience.dict())
    db.add(new_experience)
    db.commit()
    db.refresh(new_experience)
    return new_experience

@router.put("/{experience_id}", response_model=ProfessionalExperienceResponse)
def update_professionalexperience(experience_id: int, experience: ProfessionalExperienceBase, db: Session = Depends(get_db)):
    db_experience = db.query(ProfessionalExperience).filter(ProfessionalExperience.experience_id == experience_id).first()
    if db_experience is None:
        raise HTTPException(status_code=404, detail="Professional experience not found")
    
    experience_exists = db.query(ProfessionalExperience).filter(ProfessionalExperience.company == experience.company).first()
    if experience_exists:
        raise HTTPException(status_code=400, detail="Professional experience already exists")
    
    for key, value in experience.dict().items():
        setattr(db_experience, key, value)

    db.commit()
    db.refresh(db_experience)
    return db_experience

@router.delete("/{experience_id}")
def delete_professionalexperience(experience_id: int, db: Session = Depends(get_db)):
    experience = db.query(ProfessionalExperience).filter(ProfessionalExperience.experience_id == experience_id).first()
    if experience is None:
        raise HTTPException(status_code=404, detail="Professional experience not found")
    
    db.delete(experience)
    db.commit()
    return {"message": "Professional experience deleted successfully"}
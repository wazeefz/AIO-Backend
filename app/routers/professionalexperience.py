from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db 
from ..models.professionalexperience import ProfessionalExperience
from ..schemas.professionalexperience import ProfessionalExperienceBase, ProfessionalExperienceResponse

router = APIRouter(prefix="/professionalexperiences",tags=["Professional Experiences"])

@router.get("/", response_model=List[ProfessionalExperienceResponse])
def get_proex(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(ProfessionalExperience).offset(skip).limit(limit).all()

@router.get("/{experience_id}", response_model=ProfessionalExperienceResponse)
def get_proex(experience_id: int, db: Session = Depends(get_db)):
    fun = db.query(ProfessionalExperienceResponse).filter(ProfessionalExperience.experience_id == experience_id).first()
    if fun is None:
        raise HTTPException(status_code=404, detail="Professional experience not found")
    return fun

@router.post("/", response_model=ProfessionalExperienceResponse, status_code=status.HTTP_201_CREATED)
def create_proex(experience: ProfessionalExperienceBase, db: Session = Depends(get_db)):
    new_proex = ProfessionalExperience(**experience.dict())
    db.add(new_proex)
    db.commit()
    db.refresh(new_proex)
    return new_proex

@router.put("/{experience_id}", response_model=ProfessionalExperienceResponse)
def update_proex(experience_id: int, proex: ProfessionalExperienceBase, db: Session = Depends(get_db)):
    db_proex = db.query(ProfessionalExperience).filter(ProfessionalExperience.experience_id == experience_id).first()
    if db_proex is None:
        raise HTTPException(status_code=404, detail="Professional experience not found")

    for key, value in proex.dict(exclude_unset=True).items():  # Use exclude_unset=True
        setattr(db_proex, key, value)

    db.commit()
    db.refresh(db_proex)
    return db_proex

@router.delete("/{experience_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_proex(experience_id: int, db: Session = Depends(get_db)):
    proex = db.query(ProfessionalExperience).filter(ProfessionalExperience.experience_id == experience_id).first()
    if proex is None:
        raise HTTPException(status_code=404, detail="Fun fact not found")
    
    db.delete(proex)
    db.commit()
    return  # No content returned on successful delete
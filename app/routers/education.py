from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db  # Or wherever your database dependency is
from ..models.education import Education
from ..schemas.education import EducationBase, EducationResponse

router = APIRouter(prefix="/education", tags=["education"])


@router.get("/", response_model=List[EducationResponse])
def get_educations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Education).offset(skip).limit(limit).all()

@router.get("/{education_id}", response_model=EducationResponse)
def get_education(education_id: int, db: Session = Depends(get_db)):
    education = db.query(Education).filter(Education.education_id == education_id).first()
    if education is None:
        raise HTTPException(status_code=404, detail="Education entry not found")
    return education

@router.post("/", response_model=EducationResponse, status_code=status.HTTP_201_CREATED)
def create_education(education: EducationBase, db: Session = Depends(get_db)):
    if db.query(Education).filter(Education.education_id == education.education_id).first():
        raise HTTPException(status_code=400, detail="Education already exists")
    
    new_education = Education(**education.dict())
    db.add(new_education)
    db.commit()
    db.refresh(new_education)
    return new_education

@router.put("/{education_id}", response_model=EducationResponse)
def update_education(education_id: int, education: EducationBase, db: Session = Depends(get_db)):
    db_education = db.query(Education).filter(Education.education_id == education_id).first()
    if db_education is None:
        raise HTTPException(status_code=404, detail="Education entry not found")

    for key, value in education.dict(exclude_unset=True).items():  # Use exclude_unset=True
        setattr(db_education, key, value)

    db.commit()
    db.refresh(db_education)
    return db_education

@router.delete("/{education_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_education(education_id: int, db: Session = Depends(get_db)):
    education = db.query(Education).filter(Education.education_id == education_id).first()
    if education is None:
        raise HTTPException(status_code=404, detail="Education entry not found")
    
    db.delete(education)
    db.commit()
    return  # No content returned on successful delete
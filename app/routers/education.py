from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.education import Education
from ..schemas.education import EducationResponse, EducationUpdate, EducationCreate

router = APIRouter(prefix="/education", tags=["education"])

@router.get("/", response_model=List[EducationResponse])
def get_all_education(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Education).offset(skip).limit(limit).all()

@router.get("/{education_id}", response_model=EducationResponse)
def get_education(education_id: int, db: Session = Depends(get_db)):
    education = db.query(Education).filter(Education.education_id == education_id).first()
    if education is None:
        raise HTTPException(status_code=404, detail="Education record not found")
    return education

@router.get("/talent/{talent_id}", response_model=List[EducationResponse])
def get_talent_education(talent_id: int, db: Session = Depends(get_db)):
    education_records = db.query(Education).filter(Education.talent_id == talent_id).all()
    return education_records

@router.post("/", response_model=EducationResponse)
def create_education(education: EducationCreate, db: Session = Depends(get_db)):
    # Validate dates if both are provided
    if education.start_date and education.end_date:
        if education.end_date < education.start_date:
            raise HTTPException(
                status_code=400,
                detail="End date must be after start date"
            )
    
    education_data = education.model_dump()
    new_education = Education(**education_data)
    
    db.add(new_education)
    db.commit()
    db.refresh(new_education)
    return new_education

@router.put("/{education_id}", response_model=EducationResponse)
def update_education(
    education_id: int, 
    education: EducationUpdate, 
    db: Session = Depends(get_db)
):
    db_education = db.query(Education).filter(Education.education_id == education_id).first()
    if db_education is None:
        raise HTTPException(status_code=404, detail="Education record not found")

    # Get the current data
    update_data = education.model_dump(exclude_unset=True)
    
    # If updating dates, validate them
    start_date = update_data.get('start_date', db_education.start_date)
    end_date = update_data.get('end_date', db_education.end_date)
    
    if start_date and end_date and end_date < start_date:
        raise HTTPException(
            status_code=400,
            detail="End date must be after start date"
        )

    for key, value in update_data.items():
        setattr(db_education, key, value)

    db.commit()
    db.refresh(db_education)
    return db_education

@router.delete("/{education_id}")
def delete_education(education_id: int, db: Session = Depends(get_db)):
    education = db.query(Education).filter(Education.education_id == education_id).first()
    if education is None:
        raise HTTPException(status_code=404, detail="Education record not found")
    
    db.delete(education)
    db.commit()
    return {"message": "Education record deleted successfully"}

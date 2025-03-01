from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.certification import Certification
from ..schemas.certification import CertificationBase, CertificationResponse, CertificationUpdate, CertificationCreate

router = APIRouter(prefix="/certifications", tags=["certifications"])

@router.get("/", response_model=List[CertificationResponse])
def get_certifications(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Certification).offset(skip).limit(limit).all()

@router.get("/{certification_id}", response_model=CertificationResponse)
def get_certification(certification_id: int, db: Session = Depends(get_db)):
    certification = db.query(Certification).filter(Certification.certification_id == certification_id).first()
    if certification is None:
        raise HTTPException(status_code=404, detail="Certification not found")
    return certification

@router.get("/talent/{talent_id}", response_model=List[CertificationResponse])
def get_talent_certifications(talent_id: int, db: Session = Depends(get_db)):
    certifications = db.query(Certification).filter(Certification.talent_id == talent_id).all()
    return certifications

@router.post("/", response_model=CertificationResponse)
def create_certification(certification: CertificationCreate, db: Session = Depends(get_db)):
    certification_data = certification.model_dump()
    new_certification = Certification(**certification_data)
    
    db.add(new_certification)
    db.commit()
    db.refresh(new_certification)
    
    return new_certification

@router.put("/{certification_id}", response_model=CertificationResponse)
def update_certification(
    certification_id: int, 
    certification: CertificationUpdate, 
    db: Session = Depends(get_db)
):
    db_certification = db.query(Certification).filter(Certification.certification_id == certification_id).first()
    if db_certification is None:
        raise HTTPException(status_code=404, detail="Certification not found")

    certification_data = certification.model_dump(exclude_unset=True)
    for key, value in certification_data.items():
        setattr(db_certification, key, value)

    db.commit()
    db.refresh(db_certification)
    return db_certification

@router.delete("/{certification_id}")
def delete_certification(certification_id: int, db: Session = Depends(get_db)):
    certification = db.query(Certification).filter(Certification.certification_id == certification_id).first()
    if certification is None:
        raise HTTPException(status_code=404, detail="Certification not found")
    
    db.delete(certification)
    db.commit()
    return {"message": "Certification deleted successfully"}
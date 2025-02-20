from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Talent
from ..schemas.talent import TalentBase, TalentResponse, TalentUpdate

router = APIRouter(prefix="/talents", tags=["talents"])

@router.get("/", response_model=List[TalentResponse])
def get_talents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Talent).offset(skip).limit(limit).all()

@router.get("/{talent_id}", response_model=TalentResponse)
def get_talent(talent_id: int, db: Session = Depends(get_db)):
    talent = db.query(Talent).filter(Talent.talent_id == talent_id).first()
    if talent is None:
        raise HTTPException(status_code=404, detail="Talent not found")
    return talent

@router.post("/", response_model=TalentResponse)
def create_talent(talent: TalentBase, db: Session = Depends(get_db)):
    if db.query(Talent).filter(Talent.email == talent.email).first():
        raise HTTPException(status_code=400, detail="Talent already exists")

    # Convert Pydantic model to dictionary
    talent_data = talent.model_dump()  # Use `dict()` if on Pydantic v1

    new_talent = Talent(**talent_data)
    db.add(new_talent)
    db.commit()
    db.refresh(new_talent)
    
    return new_talent


@router.put("/{talent_id}", response_model=TalentResponse)
def update_talent(talent_id: int, talent: TalentUpdate, db: Session = Depends(get_db)):
    db_talent = db.query(Talent).filter(Talent.talent_id == talent_id).first()
    if db_talent is None:
        raise HTTPException(status_code=404, detail="Talent not found")

    # Only check if the email is changing
    if talent.email and talent.email != db_talent.email:
        email_exists = db.query(Talent).filter(Talent.email == talent.email).first()
        if email_exists:
            raise HTTPException(status_code=400, detail="Email already exists")

    # Update only provided fields
    talent_data = talent.model_dump(exclude_unset=True)  # Use `dict(exclude_unset=True)` if on Pydantic v1
    for key, value in talent_data.items():
        setattr(db_talent, key, value)

    db.commit()
    db.refresh(db_talent)
    return db_talent

@router.delete("/{talent_id}")
def delete_talent(talent_id: int, db: Session = Depends(get_db)):
    talent = db.query(Talent).filter(Talent.talent_id == talent_id).first()
    if talent is None:
        raise HTTPException(status_code=404, detail="Talent not found")
    
    db.delete(talent)
    db.commit()
    return {"message": "Talent deleted successfully"}

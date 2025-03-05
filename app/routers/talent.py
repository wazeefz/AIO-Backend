from fastapi import APIRouter, Depends, HTTPException, Body, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import Talent
from ..schemas.talent import TalentBase, TalentResponse, TalentUpdate
import shutil
import os
from pathlib import Path

router = APIRouter(prefix="/talents", tags=["talents"])

# Create upload directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

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
async def update_talent(
    talent_id: int, 
    talent: TalentUpdate, 
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    db_talent = db.query(Talent).filter(Talent.talent_id == talent_id).first()
    if db_talent is None:
        raise HTTPException(status_code=404, detail="Talent not found")
    
    # Check if email is being updated and if it already exists
    if talent.email and talent.email != db_talent.email:
        if db.query(Talent).filter(Talent.email == talent.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Handle file upload if provided
    if file and file.filename:
        # Delete old file if exists
        if db_talent.file_name:
            old_file_path = UPLOAD_DIR / db_talent.file_name
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
        
        # Save new file
        file_name = f"{db_talent.first_name}_{db_talent.last_name}_{file.filename}"
        file_path = UPLOAD_DIR / file_name
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Update file_name in talent data
        talent_data = talent.model_dump(exclude_unset=True)
        talent_data["file_name"] = file_name
    else:
        talent_data = talent.model_dump(exclude_unset=True)
    
    # Update talent attributes
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
    
    # Delete associated file if exists
    if talent.file_name:
        file_path = UPLOAD_DIR / talent.file_name
        if os.path.exists(file_path):
            os.remove(file_path)
    
    db.delete(talent)
    db.commit()
    return {"message": "Talent deleted successfully"}

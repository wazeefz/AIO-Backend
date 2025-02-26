from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db 
from ..models.experienceskills import ExperienceSkills
from ..schemas.experienceskills import ExperienceSkillBase, ExperienceSkillResponse

router = APIRouter(prefix="/experienceskills", tags=["experienceskills"])

@router.get("/", response_model=List[ExperienceSkillResponse])
def get_chats(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(ExperienceSkills).offset(skip).limit(limit).all()

@router.get("/{skill_id}", response_model=ExperienceSkillResponse)
def get_chat(skill_id: int, db: Session = Depends(get_db)):
    chat = db.query(ExperienceSkills).filter(ExperienceSkills.skill_id == skill_id).first()
    if chat is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return chat

@router.post("/", response_model=ExperienceSkillResponse, status_code=status.HTTP_201_CREATED)
def create_experienceskill(chat: ExperienceSkillBase, db: Session = Depends(get_db)):
    if db.query(ExperienceSkills).filter(ExperienceSkills.skill_id == ExperienceSkills.skill_id).first():
        raise HTTPException(status_code=400, detail="Skill already exists")
    
    new_experienceskill = ExperienceSkills(**chat.dict())
    db.add(new_experienceskill)
    db.commit()
    db.refresh(new_experienceskill)
    return new_experienceskill

@router.put("/{skill_id}", response_model=ExperienceSkillResponse)
def update_experienceskill(skill_id: int, experienceskills: ExperienceSkillBase, db: Session = Depends(get_db)):
    db_experienceskill = db.query(ExperienceSkills).filter(ExperienceSkills.skill_id == skill_id).first()
    if db_experienceskill is None:
        raise HTTPException(status_code=404, detail="Chat not found")

    for key, value in experienceskills.dict(exclude_unset=True).items():  # Use exclude_unset=True
        setattr(db_experienceskill, key, value)

    db.commit()
    db.refresh(db_experienceskill)
    return db_experienceskill

@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat(skill_id: int, db: Session = Depends(get_db)):
    chat = db.query(ExperienceSkills).filter(ExperienceSkills.skill_id == skill_id).first()
    if chat is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    db.delete(chat)
    db.commit()
    return  # No content returned on successful delete
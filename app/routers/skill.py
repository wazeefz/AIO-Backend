from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Skill
from ..schemas.skill import SkillCreate, SkillResponse, SkillUpdate

router = APIRouter(prefix="/skills", tags=["skills"])

@router.get("/", response_model=List[SkillResponse])
def get_skills(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Skill).offset(skip).limit(limit).all()

@router.get("/{skill_id}", response_model=SkillResponse)
def get_skill(skill_id: int, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.skill_id == skill_id).one_or_none()
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill

@router.post("/", response_model=SkillResponse, status_code=201)
def create_skill(skill: SkillCreate, db: Session = Depends(get_db)):
    if db.query(Skill).filter(Skill.skill_name == skill.skill_name).first():
        raise HTTPException(status_code=400, detail="Skill already exists")
    
    new_skill = Skill(**skill.model_dump())  # Use `model_dump()` instead of `dict()`
    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)
    return new_skill

@router.put("/{skill_id}", response_model=SkillResponse)
def update_skill(skill_id: int, skill: SkillUpdate, db: Session = Depends(get_db)):
    db_skill = db.query(Skill).filter(Skill.skill_id == skill_id).one_or_none()
    if db_skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    # Ensure skill name uniqueness but exclude the current skill
    if skill.skill_name:
        existing_skill = db.query(Skill).filter(
            Skill.skill_name == skill.skill_name,
            Skill.skill_id != skill_id  # Ensure it's not the same skill
        ).first()
        if existing_skill:
            raise HTTPException(status_code=400, detail="Skill name already exists")

    # Update fields dynamically
    for key, value in skill.model_dump(exclude_unset=True).items():
        setattr(db_skill, key, value)

    db.commit()
    db.refresh(db_skill)
    return db_skill

@router.delete("/{skill_id}", status_code=204)
def delete_skill(skill_id: int, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.skill_id == skill_id).one_or_none()
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    db.delete(skill)
    db.commit()
    return {"message": "Skill deleted successfully"}

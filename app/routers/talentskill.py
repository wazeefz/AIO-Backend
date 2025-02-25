from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..database import get_db
from ..models.talent import Talent
from ..models.skill import Skill
from ..models.talentskill import TalentSkill
from ..schemas import talentskill as schemas

router = APIRouter(
    prefix="/talentskills",
    tags=["Talent Skills"]
)

@router.post("/", response_model=schemas.TalentSkillResponse, status_code=status.HTTP_201_CREATED)
def create_talent_skill(talent_skill: schemas.TalentSkillCreate, db: Session = Depends(get_db)):
    # Check if talent exists
    db_talent = db.query(Talent).filter(Talent.talent_id == talent_skill.talent_id).first()
    if not db_talent:
        raise HTTPException(status_code=404, detail="Talent not found")
    
    # Check if skill exists
    db_skill = db.query(Skill).filter(Skill.skill_id == talent_skill.skill_id).first()
    if not db_skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    # Check if the talent-skill combination already exists
    existing_talent_skill = db.query(TalentSkill).filter(
        TalentSkill.talent_id == talent_skill.talent_id,
        TalentSkill.skill_id == talent_skill.skill_id
    ).first()
    if existing_talent_skill:
        raise HTTPException(status_code=400, detail="This talent already has this skill")
    
    # Validate proficiency level (assuming 1-5 scale)
    if not 1 <= talent_skill.proficiency_level <= 5:
        raise HTTPException(status_code=400, detail="Proficiency level must be between 1 and 5")
    
    # Validate years of experience (non-negative)
    if talent_skill.years_of_experience < 0:
        raise HTTPException(status_code=400, detail="Years of experience cannot be negative")
    
    # Create new talent skill
    db_talent_skill = TalentSkill(**talent_skill.model_dump())
    db.add(db_talent_skill)
    db.commit()
    db.refresh(db_talent_skill)
    return db_talent_skill

@router.get("/talent/{talent_id}/skill/{skill_id}", response_model=schemas.TalentSkillResponse)
def get_talent_skill(talent_id: int, skill_id: int, db: Session = Depends(get_db)):
    db_talent_skill = db.query(TalentSkill).filter(
        TalentSkill.talent_id == talent_id,
        TalentSkill.skill_id == skill_id
    ).first()
    if not db_talent_skill:
        raise HTTPException(status_code=404, detail="Talent skill not found")
    return db_talent_skill

@router.get("/talent/{talent_id}", response_model=List[schemas.TalentSkillResponse])
def get_talent_skills(
    talent_id: int, 
    min_proficiency: int = Query(None, ge=1, le=5),
    min_experience: float = Query(None, ge=0),
    db: Session = Depends(get_db)
):
    # Check if talent exists
    db_talent = db.query(Talent).filter(Talent.talent_id == talent_id).first()
    if not db_talent:
        raise HTTPException(status_code=404, detail="Talent not found")

    # Base query
    query = db.query(TalentSkill).filter(TalentSkill.talent_id == talent_id)
    
    # Apply filters if provided
    if min_proficiency is not None:
        query = query.filter(TalentSkill.proficiency_level >= min_proficiency)
    if min_experience is not None:
        query = query.filter(TalentSkill.years_of_experience >= min_experience)
    
    return query.all()

@router.get("/skill/{skill_id}", response_model=List[schemas.TalentSkillResponse])
def get_talents_by_skill(
    skill_id: int,
    min_proficiency: int = Query(None, ge=1, le=5),
    min_experience: float = Query(None, ge=0),
    db: Session = Depends(get_db)
):
    # Check if skill exists
    db_skill = db.query(Skill).filter(Skill.skill_id == skill_id).first()
    if not db_skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    # Base query
    query = db.query(TalentSkill).filter(TalentSkill.skill_id == skill_id)
    
    # Apply filters if provided
    if min_proficiency is not None:
        query = query.filter(TalentSkill.proficiency_level >= min_proficiency)
    if min_experience is not None:
        query = query.filter(TalentSkill.years_of_experience >= min_experience)
    
    return query.all()

@router.put("/talent/{talent_id}/skill/{skill_id}", response_model=schemas.TalentSkillResponse)
def update_talent_skill(
    talent_id: int,
    skill_id: int,
    talent_skill: schemas.TalentSkillUpdate,
    db: Session = Depends(get_db)
):
    db_talent_skill = db.query(TalentSkill).filter(
        TalentSkill.talent_id == talent_id,
        TalentSkill.skill_id == skill_id
    ).first()
    if not db_talent_skill:
        raise HTTPException(status_code=404, detail="Talent skill not found")
    
    # Validate proficiency level if provided
    if talent_skill.proficiency_level is not None:
        if not 1 <= talent_skill.proficiency_level <= 5:
            raise HTTPException(status_code=400, detail="Proficiency level must be between 1 and 5")
    
    # Validate years of experience if provided
    if talent_skill.years_of_experience is not None:
        if talent_skill.years_of_experience < 0:
            raise HTTPException(status_code=400, detail="Years of experience cannot be negative")
    
    update_data = talent_skill.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_talent_skill, field, value)
    
    db.commit()
    db.refresh(db_talent_skill)
    return db_talent_skill

@router.delete("/talent/{talent_id}/skill/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_talent_skill(talent_id: int, skill_id: int, db: Session = Depends(get_db)):
    db_talent_skill = db.query(TalentSkill).filter(
        TalentSkill.talent_id == talent_id,
        TalentSkill.skill_id == skill_id
    ).first()
    if not db_talent_skill:
        raise HTTPException(status_code=404, detail="Talent skill not found")
    
    db.delete(db_talent_skill)
    db.commit()
    return None

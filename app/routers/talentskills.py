# from fastapi import APIRouter, Depends, HTTPException, status, Query
# from sqlalchemy.orm import Session
# from typing import List

# from ..database import get_db  # Or wherever your database dependency is
# from ..models.talentskills import TalentSkill
# from ..schemas.talentskills import TalentSkillBase, TalentSkillResponse

# @router.get("/", response_model=List[TalentSkillResponse])
# def get_talentskill(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     return db.query(TalentSkill).offset(skip).limit(limit).all()

# @router.get("/{talent_id}", response_model=TalentSkillResponse)
# def get_talentskill(talent_id: int, db: Session = Depends(get_db)):
#     talentskill = db.query(TalentSkill).filter(TalentSkill.talent_id == talent_id).first()
#     if talentskill is None:
#         raise HTTPException(status_code=404, detail="Talent skill entry not found")
#     return talentskill

# @router.post("/", response_model=TalentSkillResponse, status_code=status.HTTP_201_CREATED)
# def create_talentskill(talentskill: TalentSkillBase, db: Session = Depends(get_db)):
#     if db.query(TalentSkill).filter(TalentSkill.talent_id == talentskill.talent_id).first():
#         raise HTTPException(status_code=400, detail="Talent skill already exists")
    
#     new_talentskill = TalentSkill(**talentskill.dict())
#     db.add(new_talentskill)
#     db.commit()
#     db.refresh(new_talentskill)
#     return new_talentskill

# @router.put("/{talent_id}", response_model=TalentSkillResponse)
# def update_talentskill(talent_id: int, talentskill: TalentSkillBase, db: Session = Depends(get_db)):
#     db_talentskill = db.query(TalentSkill).filter(TalentSkill.talent_id == talent_id).first()
#     if db_talentskill is None:
#         raise HTTPException(status_code=404, detail="Talent skill entry not found")

#     for key, value in talentskill.dict(exclude_unset=True).items():  # Use exclude_unset=True
#         setattr(db_talentskill, key, value)

#     db.commit()
#     db.refresh(db_talentskill)
#     return db_talentskill

# @router.delete("/{talent_id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_talentskill(talent_id: int, db: Session = Depends(get_db)):
#     talentskill = db.query(TalentSkill).filter(TalentSkill.talent_id == talent_id).first()
#     if talentskill is None:
#         raise HTTPException(status_code=404, detail="Talent skill entry not found")
    
#     db.delete(talentskill)
#     db.commit()
#     return  # No content returned on successful delete
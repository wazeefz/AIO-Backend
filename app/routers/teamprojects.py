from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.teamprojects import TeamProjects
from ..schemas.teamprojects import TeamProjectsBase, TeamProjectsResponse, TeamProjectsCreate, TeamProjectsUpdate

router = APIRouter(prefix="/teamprojects", tags=["teamprojects"])

@router.get("/", response_model=List[TeamProjectsResponse])
def get_teamprojects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(TeamProjects).offset(skip).limit(limit).all()

@router.get("/{project_id}", response_model=TeamProjectsResponse)
def get_teamproject(project_id: int, db: Session = Depends(get_db)):
    teamproject = db.query(TeamProjects).filter(TeamProjects.project_id == project_id).first()
    if teamproject is None:
        raise HTTPException(status_code=404, detail="TeamProject not found")
    return teamproject

@router.post("/", response_model=TeamProjectsResponse)
def create_teamproject(teamproject: TeamProjectsBase, db: Session = Depends(get_db)):
    if db.query(TeamProjects).filter(TeamProjects.project_id == teamproject.project_id).first():
        raise HTTPException(status_code=400, detail="TeamProject already exists")
    
    new_teamproject = TeamProjects(**teamproject.dict())
    db.add(new_teamproject)
    db.commit()
    db.refresh(new_teamproject)
    return new_teamproject

@router.put("/{project_id}", response_model=TeamProjectsResponse)
def update_teamproject(project_id: int, teamproject: TeamProjectsBase, db: Session = Depends(get_db)):
    db_teamproject = db.query(TeamProjects).filter(TeamProjects.project_id == project_id).first()
    if db_teamproject is None:
        raise HTTPException(status_code=404, detail="TeamProject not found")
    
    for key, value in teamproject.dict().items():
        setattr(db_teamproject, key, value)

    db.commit()
    db.refresh(db_teamproject)
    return db_teamproject

@router.delete("/{project_id}")
def delete_teamproject(project_id: int, db: Session = Depends(get_db)):
    teamproject = db.query(TeamProjects).filter(TeamProjects.project_id == project_id).first()
    if teamproject is None:
        raise HTTPException(status_code=404, detail="TeamProject not found")
    
    db.delete(teamproject)
    db.commit()
    return {"message": "TeamProject deleted successfully"}

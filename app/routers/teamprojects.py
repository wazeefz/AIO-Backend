from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db  # Or wherever your database dependency is
from ..models.teamprojects import TeamProjects
from ..schemas.teamprojects import TeamProjectBase, TeamProjectResponse

router = APIRouter(prefix="/teamproject", tags=["teamproject"])


@router.get("/", response_model=List[TeamProjectResponse])
def get_team(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(TeamProjects).offset(skip).limit(limit).all()

@router.get("/{project_id}", response_model=TeamProjectResponse)
def get_team(project_id: int, db: Session = Depends(get_db)):
    team = db.query(TeamProjects).filter(TeamProjects.project_id == project_id).first()
    if team is None:
        raise HTTPException(status_code=404, detail="Team projects entry not found")
    return team

@router.post("/", response_model=TeamProjectResponse, status_code=status.HTTP_201_CREATED)
def create_team(teamproject: TeamProjectBase, db: Session = Depends(get_db)):
    if db.query(TeamProjects).filter(TeamProjects.project_id == teamproject.project_id).first():
        raise HTTPException(status_code=400, detail="Team project already exists")
    
    new_team = TeamProjects(**teamproject.dict())
    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    return new_team

@router.put("/{project_id}", response_model=TeamProjectResponse)
def update_team(project_id: int, teamproject: TeamProjectBase, db: Session = Depends(get_db)):
    db_team = db.query(TeamProjects).filter(TeamProjects.project_id == project_id).first()
    if db_team is None:
        raise HTTPException(status_code=404, detail="Team project entry not found")

    for key, value in teamproject.dict(exclude_unset=True).items():  # Use exclude_unset=True
        setattr(db_team, key, value)

    db.commit()
    db.refresh(db_team)
    return db_team

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(project_id: int, db: Session = Depends(get_db)):
    teamproject = db.query(TeamProjects).filter(TeamProjects.project_id == project_id).first()
    if teamproject is None:
        raise HTTPException(status_code=404, detail="Team project entry not found")
    
    db.delete(teamproject)
    db.commit()
    return  # No content returned on successful delete
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.projectsassignment import ProjectAssignment
from ..schemas.projectsassignment import ProjectAssignmentBase, ProjectAssignmentResponse, ProjectAssignmentCreate, ProjectAssignmentUpdate

router = APIRouter(prefix="/projectsassignment", tags=["projectsassignment"])

@router.get("/", response_model=List[ProjectAssignmentResponse])
def get_projectsassignment(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(ProjectAssignment).offset(skip).limit(limit).all()

@router.get("/{assignment_id}", response_model=ProjectAssignmentResponse)
def get_projectassignment(assignment_id: int, db: Session = Depends(get_db)):
    projectassignment = db.query(ProjectAssignment).filter(ProjectAssignment.assignment_id == assignment_id).first()
    if projectassignment is None:
        raise HTTPException(status_code=404, detail="Project assignment not found")
    return projectassignment

@router.post("/", response_model=ProjectAssignmentResponse)
def create_projectassignment(projectassignment: ProjectAssignmentBase, db: Session = Depends(get_db)):
    if db.query(ProjectAssignment).filter(ProjectAssignment.project_id == projectassignment.project_id).first():
        raise HTTPException(status_code=400, detail="Project assignment already exists")
    
    new_projectassignment = ProjectAssignment(**projectassignment.dict())
    db.add(new_projectassignment)
    db.commit()
    db.refresh(new_projectassignment)
    return new_projectassignment

@router.put("/{assignment_id}", response_model=ProjectAssignmentResponse)
def update_projectassignment(assignment_id: int, projectassignment: ProjectAssignmentBase, db: Session = Depends(get_db)):
    db_projectassignment = db.query(ProjectAssignment).filter(ProjectAssignment.assignment_id == assignment_id).first()
    if db_projectassignment is None:
        raise HTTPException(status_code=404, detail="Project assignment not found")
    
    projectassignment_exists = db.query(ProjectAssignment).filter(ProjectAssignment.project_id == projectassignment.project_id).first()
    if projectassignment_exists:
        raise HTTPException(status_code=400, detail="Project assignment already exists")
    
    for key, value in projectassignment.dict().items():
        setattr(db_projectassignment, key, value)

    db.commit()
    db.refresh(db_projectassignment)
    return db_projectassignment

@router.delete("/{assignment_id}")
def delete_projectassignment(assignment_id: int, db: Session = Depends(get_db)):
    projectassignment = db.query(ProjectAssignment).filter(ProjectAssignment.assignment_id == assignment_id).first()
    if projectassignment is None:
        raise HTTPException(status_code=404, detail="Project assignment not found")
    
    db.delete(projectassignment)
    db.commit()
    return {"message": "Project assignment deleted successfully"}

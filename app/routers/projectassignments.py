from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import ProjectAssignment, Project, Talent
from ..schemas.projectassignments import (
    ProjectAssignmentCreate,
    ProjectAssignmentResponse,
    ProjectAssignmentUpdate,
)

router = APIRouter(prefix="/project-assignments", tags=["project-assignments"])

@router.get("/", response_model=List[ProjectAssignmentResponse])
def get_all_project_assignments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(ProjectAssignment).offset(skip).limit(limit).all()


@router.post("/", response_model=ProjectAssignmentResponse)
def create_project_assignment(
    assignment: ProjectAssignmentCreate,
    db: Session = Depends(get_db)
):
    """Assign a talent to a project"""
    # Check if project and talent exist
    project = db.query(Project).filter(Project.project_id == assignment.project_id).first()
    talent = db.query(Talent).filter(Talent.talent_id == assignment.talent_id).first()
    
    if not project or not talent:
        raise HTTPException(status_code=404, detail="Project or Talent not found")
    
    # Check if assignment already exists
    existing_assignment = db.query(ProjectAssignment).filter(
        ProjectAssignment.project_id == assignment.project_id,
        ProjectAssignment.talent_id == assignment.talent_id
    ).first()
    
    if existing_assignment:
        raise HTTPException(status_code=400, detail="Assignment already exists")
    
    new_assignment = ProjectAssignment(**assignment.model_dump())
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    return new_assignment

@router.delete("/{project_id}/{talent_id}")
def remove_team_member(project_id: int, talent_id: int, db: Session = Depends(get_db)):
    """Remove a talent from a project"""
    assignment = db.query(ProjectAssignment).filter(
        ProjectAssignment.project_id == project_id,
        ProjectAssignment.talent_id == talent_id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    db.delete(assignment)
    db.commit()
    return {"message": "Team member removed successfully"}

@router.put("/{project_id}/{talent_id}", response_model=ProjectAssignmentResponse)
def update_project_assignment(
    project_id: int,
    talent_id: int,
    assignment_update: ProjectAssignmentUpdate,
    db: Session = Depends(get_db)
):
    """Update a project assignment"""
    assignment = db.query(ProjectAssignment).filter(
        ProjectAssignment.project_id == project_id,
        ProjectAssignment.talent_id == talent_id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Update only provided fields
    update_data = assignment_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(assignment, key, value)
    
    db.commit()
    db.refresh(assignment)
    return assignment


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import ProjectAssignments, Project, Talent
from ..schemas.projectassignments import (
    ProjectAssignmentCreate,
    ProjectAssignmentResponse,
    ProjectAssignmentUpdate,
    ProjectAssignmentExtendedResponse
)

router = APIRouter(prefix="/project-assignments", tags=["project-assignments"])

@router.get("/", response_model=List[ProjectAssignmentExtendedResponse])
def get_all_project_assignments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(ProjectAssignments).offset(skip).limit(limit).all()

@router.get("/project/{project_id}/team", response_model=List[ProjectAssignmentExtendedResponse])
def get_project_team(project_id: int, db: Session = Depends(get_db)):
    """Get all team members assigned to a specific project"""
    assignments = db.query(ProjectAssignments).filter(
        ProjectAssignments.project_id == project_id
    ).all()
    if not assignments:
        return []
    return assignments

@router.get("/available-talents/{project_id}", response_model=List[dict])
def get_available_talents(project_id: int, db: Session = Depends(get_db)):
    """Get all talents not assigned to the specified project"""
    # Get IDs of talents already assigned to the project
    assigned_talents = db.query(ProjectAssignments.talent_id).filter(
        ProjectAssignments.project_id == project_id
    ).all()
    assigned_talent_ids = [talent[0] for talent in assigned_talents]
    
    # Query talents not in the project
    available_talents = db.query(Talent).filter(
        Talent.talent_id.notin_(assigned_talent_ids)
    ).all()
    
    return available_talents

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
    existing_assignment = db.query(ProjectAssignments).filter(
        ProjectAssignments.project_id == assignment.project_id,
        ProjectAssignments.talent_id == assignment.talent_id
    ).first()
    
    if existing_assignment:
        raise HTTPException(status_code=400, detail="Assignment already exists")
    
    new_assignment = ProjectAssignments(**assignment.model_dump())
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    return new_assignment

@router.delete("/{project_id}/{talent_id}")
def remove_team_member(project_id: int, talent_id: int, db: Session = Depends(get_db)):
    """Remove a talent from a project"""
    assignment = db.query(ProjectAssignments).filter(
        ProjectAssignments.project_id == project_id,
        ProjectAssignments.talent_id == talent_id
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
    assignment = db.query(ProjectAssignments).filter(
        ProjectAssignments.project_id == project_id,
        ProjectAssignments.talent_id == talent_id
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

@router.post("/batch-assign/{project_id}")
def batch_assign_team_members(project_id: int, talent_ids: List[int], db: Session = Depends(get_db)):
    """Batch assign multiple talents to a project"""
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    new_assignments = []
    for talent_id in talent_ids:
        # Check if talent exists
        talent = db.query(Talent).filter(Talent.talent_id == talent_id).first()
        if not talent:
            continue
            
        # Check if assignment already exists
        existing = db.query(ProjectAssignments).filter(
            ProjectAssignments.project_id == project_id,
            ProjectAssignments.talent_id == talent_id
        ).first()
        
        if not existing:
            new_assignment = ProjectAssignments(
                project_id=project_id,
                talent_id=talent_id
            )
            db.add(new_assignment)
            new_assignments.append(new_assignment)
    
    db.commit()
    return {"message": f"Added {len(new_assignments)} team members to the project"}

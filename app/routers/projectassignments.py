from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from typing import List
from ..database import get_db
from ..models import ProjectAssignment, Project, Talent
from ..schemas.projectassignments import (
    ProjectAssignmentCreate,
    ProjectAssignmentResponse,
    ProjectAssignmentUpdate,
    ProjectTeamMemberResponse,
    AvailableTalentResponse
)

router = APIRouter(prefix="/project-assignments", tags=["project-assignments"])

@router.get("/", response_model=List[ProjectAssignmentResponse])
def get_all_project_assignments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(ProjectAssignment).offset(skip).limit(limit).all()

@router.get("/project/{project_id}/team", response_model=List[ProjectTeamMemberResponse])
def get_project_team(project_id: int, db: Session = Depends(get_db)):
    """Get all team members assigned to a specific project with essential information"""
    # First check if project exists
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Query assignments with joined talent information
    team_members = (
        db.query(
            ProjectAssignment.talent_id,
            ProjectAssignment.role,
            ProjectAssignment.performance_rating,
            ProjectAssignment.assignment_start_date,
            ProjectAssignment.assignment_end_date,
            Talent.first_name,
            Talent.last_name,
            Talent.job_title,
            Talent.email
        )
        .join(Talent)
        .filter(ProjectAssignment.project_id == project_id)
        .all()
    )
    
    # Transform the results to match the response model
    result = []
    for member in team_members:
        team_member = {
            "talent_id": member.talent_id,
            "first_name": member.first_name,
            "last_name": member.last_name,
            "job_title": member.job_title or "Not Specified",
            "role": member.role,
            "email": member.email,
            "performance_rating": member.performance_rating,
            "assignment_start_date": member.assignment_start_date,
            "assignment_end_date": member.assignment_end_date
        }
        result.append(team_member)
    
    return result

@router.get("/available-talents/{project_id}", response_model=List[AvailableTalentResponse])
def get_available_talents(project_id: int, db: Session = Depends(get_db)):
    """Get all talents not assigned to the specified project with complete information"""
    # Get IDs of talents already assigned to the project
    assigned_talents = (
        select(ProjectAssignment.talent_id)
        .where(ProjectAssignment.project_id == project_id)
        .scalar_subquery()
    )
    
    # Query talents not in the project with all their information
    available_talents = (
        db.query(Talent)
        .options(joinedload(Talent.department))  # Include department relationship if needed
        .filter(~Talent.talent_id.in_(assigned_talents))
        .all()
    )
    
    return available_talents  # FastAPI will handle the conversion to AvailableTalentResponse

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
        existing = db.query(ProjectAssignment).filter(
            ProjectAssignment.project_id == project_id,
            ProjectAssignment.talent_id == talent_id
        ).first()
        
        if not existing:
            new_assignment = ProjectAssignment(
                project_id=project_id,
                talent_id=talent_id
            )
            db.add(new_assignment)
            new_assignments.append(new_assignment)
    
    db.commit()
    return {"message": f"Added {len(new_assignments)} team members to the project"}

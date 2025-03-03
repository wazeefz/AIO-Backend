from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List
from ..database import get_db
from ..models import ProjectAssignment, Project, Talent, Department, TalentSkill, Skill
from ..schemas.profileCard import (
    ProjectTeamMemberResponse,
    AvailableTalentResponse
)

router = APIRouter(prefix="/profile-card", tags=["Profile Card"])
                   
# To be used for getting all members of an assigned project 
@router.get("/project/{project_id}/team", response_model=List[ProjectTeamMemberResponse])
def get_project_team(project_id: int, db: Session = Depends(get_db)):
    """Get all team members assigned to a specific project with essential information"""
    # First check if project exists
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get team members with their department information
    team_members = (
        db.query(
            Talent,
            Department.department_name.label('department_name'),
            ProjectAssignment.role,
            ProjectAssignment.performance_rating,
            ProjectAssignment.assignment_start_date,
            ProjectAssignment.assignment_end_date
        )
        .join(ProjectAssignment, ProjectAssignment.talent_id == Talent.talent_id)
        .join(Department, Department.department_id == Talent.department_id)
        .filter(ProjectAssignment.project_id == project_id)
        .all()
    )
    
    # Transform the results to match the response schema
    result = []
    for (talent, department_name, role, performance_rating, 
         assignment_start_date, assignment_end_date) in team_members:
        
        # Get skills for this talent
        talent_skills = (
            db.query(Skill.skill_name)
            .join(TalentSkill, TalentSkill.skill_id == Skill.skill_id)
            .filter(TalentSkill.talent_id == talent.talent_id)
            .all()
        )
        
        team_member_dict = {
            "talent_id": talent.talent_id,
            "first_name": talent.first_name,
            "last_name": talent.last_name,
            "email": talent.email,
            "basic_salary": talent.basic_salary,
            "phone": talent.phone,
            "job_title": talent.job_title,
            "department_name": department_name,
            "role": role,
            "performance_rating": performance_rating,
            "assignment_start_date": assignment_start_date,
            "assignment_end_date": assignment_end_date,
            "total_experience_years": talent.total_experience_years,
            "skills": [skill[0] for skill in talent_skills]  # Extract skill names from result tuples
        }
        result.append(team_member_dict)
    
    return result
    

#To be used to see what members are available to be assigned to a project
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
        db.query(
            Talent,
            Department.department_name.label('department_name')
        )
        .join(Department, Department.department_id == Talent.department_id)
        .filter(~Talent.talent_id.in_(assigned_talents))
        .all()
    )
    
    # Transform the results to match the response schema
    result = []
    for talent, department_name in available_talents:
        # Get skills for this talent
        talent_skills = (
            db.query(Skill.skill_name)
            .join(TalentSkill, TalentSkill.skill_id == Skill.skill_id)
            .filter(TalentSkill.talent_id == talent.talent_id)
            .all()
        )
        
        talent_dict = {
            "talent_id": talent.talent_id,
            "first_name": talent.first_name,
            "last_name": talent.last_name,
            "email": talent.email,
            "basic_salary": talent.basic_salary,
            "phone": talent.phone,
            "job_title": talent.job_title,
            "department_name": department_name,
            "total_experience_years": talent.total_experience_years,
            "skills": [skill[0] for skill in talent_skills]  # Extract skill names from result tuples
        }
        result.append(talent_dict)
    
    return result
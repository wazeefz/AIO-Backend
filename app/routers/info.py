from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List
from ..database import get_db
from ..models import ProjectAssignment, Project, Talent, Department, TalentSkill, Skill
from ..schemas.info import (
   EmployeeInfoResponse
)

router = APIRouter(prefix="/info", tags=["Employee Info"])
                   
# To be used for getting all members of an assigned project 
@router.get("/", response_model=List[EmployeeInfoResponse])
def get_info(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):

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
    
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from . import database, models

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for response schemas
class DepartmentBase(BaseModel):
    department_name: str

class DepartmentSchema(DepartmentBase):
    department_id: int

    class Config:
        orm_mode = True

class SkillBase(BaseModel):
    skill_name: str
    skill_category: str

class SkillSchema(SkillBase):
    skill_id: int

    class Config:
        orm_mode = True

class TalentBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    job_title: str
    employment_type: str
    department_id: int
    hire_date: datetime
    basic_salary: float
    gender: str
    date_of_birth: datetime
    marital_status: bool
    total_experience_years: float
    career_preferences: str
    availability_status: str

class TalentSchema(TalentBase):
    talent_id: int

    class Config:
        orm_mode = True

class ProjectBase(BaseModel):
    name: str
    starred: bool
    cv_count: int
    progress: int
    status: str
    budget: float
    user_id: int
    start_date: datetime
    required_skills: List[int]
    min_experience_years: int
    team_size: int
    project_description: str

class ProjectSchema(ProjectBase):
    project_id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    name: str
    department_id: int
    email: str
    role: str

class UserSchema(UserBase):
    user_id: int

    class Config:
        orm_mode = True

# API Endpoints
@app.get("/departments/", response_model=List[DepartmentSchema])
def get_departments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db)
):
    departments = db.query(models.Department).offset(skip).limit(limit).all()
    return departments

@app.get("/departments/{department_id}", response_model=DepartmentSchema)
def get_department(department_id: int, db: Session = Depends(database.get_db)):
    department = db.query(models.Department).filter(models.Department.department_id == department_id).first()
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    return department

@app.get("/skills/", response_model=List[SkillSchema])
def get_skills(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db)
):
    skills = db.query(models.Skill).offset(skip).limit(limit).all()
    return skills

@app.get("/skills/{skill_id}", response_model=SkillSchema)
def get_skill(skill_id: int, db: Session = Depends(database.get_db)):
    skill = db.query(models.Skill).filter(models.Skill.skill_id == skill_id).first()
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill

@app.get("/talents/", response_model=List[TalentSchema])
def get_talents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db)
):
    talents = db.query(models.Talent).offset(skip).limit(limit).all()
    return talents

@app.get("/talents/{talent_id}", response_model=TalentSchema)
def get_talent(talent_id: int, db: Session = Depends(database.get_db)):
    talent = db.query(models.Talent).filter(models.Talent.talent_id == talent_id).first()
    if talent is None:
        raise HTTPException(status_code=404, detail="Talent not found")
    return talent

@app.get("/projects/", response_model=List[ProjectSchema])
def get_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db)
):
    projects = db.query(models.Project).offset(skip).limit(limit).all()
    return projects

@app.get("/projects/{project_id}", response_model=ProjectSchema)
def get_project(project_id: int, db: Session = Depends(database.get_db)):
    project = db.query(models.Project).filter(models.Project.project_id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.get("/users/", response_model=List[UserSchema])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db)
):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=UserSchema)
def get_user(user_id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
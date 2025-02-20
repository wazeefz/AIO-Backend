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

# Departments
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

@app.post("/departments/", response_model=DepartmentSchema)
def create_department(department: DepartmentBase, db: Session = Depends(database.get_db)):
    if db.query(models.Department).filter(models.Department.department_name == department.department_name).first():
        raise HTTPException(status_code=400, detail="Department already exists")
    
    new_department = models.Department(**department.dict())
    db.add(new_department)
    db.commit()
    db.refresh(new_department)
    return new_department

@app.put("/departments/{department_id}", response_model=DepartmentSchema)
def update_department(department_id: int, department: DepartmentBase, db: Session = Depends(database.get_db)):
    db_department = db.query(models.Department).filter(models.Department.department_id == department_id).first()
    if db_department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    
    username_exists = db.query(models.Department).filter(models.Department.department_name == department.department_name).first()
    if username_exists:
        raise HTTPException(status_code=400, detail="Department name already exists")
    
    for key, value in department.dict().items():
        setattr(db_department, key, value)

    db.commit()
    db.refresh(db_department)
    return db_department

@app.delete("/departments/{department_id}")
def delete_department(department_id: int, db: Session = Depends(database.get_db)):
    department = db.query(models.Department).filter(models.Department.department_id == department_id).first()
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    
    db.delete(department)
    db.commit()
    return {"message": "Department deleted successfully"}

# Skills
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

@app.post("/skills/", response_model=SkillSchema)
def create_skill(skill: SkillBase, db: Session = Depends(database.get_db)):
    if db.query(models.Skill).filter(models.Skill.skill_name == skill.skill_name).first():
        raise HTTPException(status_code=400, detail="Skill already exists")
    
    new_skill = models.Skill(**skill.dict())
    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)
    return new_skill

@app.put("/skills/{skill_id}", response_model=SkillSchema)
def update_skill(skill_id: int, skill: SkillBase, db: Session = Depends(database.get_db)):
    db_skill = db.query(models.Skill).filter(models.Skill.skill_id == skill_id).first()
    if db_skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    username_exists = db.query(models.Skill).filter(models.Skill.skill_name == skill.skill_name).first()
    if username_exists:
        raise HTTPException(status_code=400, detail="Skill name already exists")
    
    for key, value in skill.dict().items():
        setattr(db_skill, key, value)

    db.commit()
    db.refresh(db_skill)
    return db_skill

@app.delete("/skills/{skill_id}")
def delete_skill(skill_id: int, db: Session = Depends(database.get_db)):
    skill = db.query(models.Skill).filter(models.Skill.skill_id == skill_id).first()
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    db.delete(skill)
    db.commit()
    return {"message": "Skill deleted successfully"}

# Talents
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

@app.post("/talents/", response_model=TalentSchema)
def create_talent(talent: TalentBase, db: Session = Depends(database.get_db)):
    if db.query(models.Talent).filter(models.Talent.email == talent.email).first():
        raise HTTPException(status_code=400, detail="Talent already exists")
    
    new_talent = models.Talent(**talent.dict())
    db.add(new_talent)
    db.commit()
    db.refresh(new_talent)
    return new_talent

@app.put("/talents/{talent_id}", response_model=TalentSchema)
def update_talent(talent_id: int, talent: TalentBase, db: Session = Depends(database.get_db)):
    db_talent = db.query(models.Talent).filter(models.Talent.talent_id == talent_id).first()
    if db_talent is None:
        raise HTTPException(status_code=404, detail="Talent not found")
    
    email_exists = db.query(models.Talent).filter(models.Talent.email == talent.email).first()
    if email_exists:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    for key, value in talent.dict().items():
        setattr(db_talent, key, value)

    db.commit()
    db.refresh(db_talent)
    return db_talent

@app.delete("/talents/{talent_id}")
def delete_talent(talent_id: int, db: Session = Depends(database.get_db)):
    talent = db.query(models.Talent).filter(models.Talent.talent_id == talent_id).first()
    if talent is None:
        raise HTTPException(status_code=404, detail="Talent not found")
    
    db.delete(talent)
    db.commit()
    return {"message": "Talent deleted successfully"}

# Projects
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

@app.post("/projects/", response_model=ProjectSchema)
def create_project(project: ProjectBase, db: Session = Depends(database.get_db)):
    if db.query(models.Project).filter(models.Project.name == project.name).first():
        raise HTTPException(status_code=400, detail="Project already exists")
    
    new_project = models.Project(**project.dict())
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

@app.put("/projects/{project_id}", response_model=ProjectSchema)
def update_project(project_id: int, project: ProjectBase, db: Session = Depends(database.get_db)):
    db_project = db.query(models.Project).filter(models.Project.project_id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project_exists = db.query(models.Project).filter(models.Project.name == project.name).first()
    if project_exists:
        raise HTTPException(status_code=400, detail="Project name already exists")
    
    for key, value in project.dict().items():
        setattr(db_project, key, value)

    db.commit()
    db.refresh(db_project)
    return db_project

@app.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(database.get_db)):
    project = db.query(models.Project).filter(models.Project.project_id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}

# Users
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

@app.post("/users/", response_model=UserSchema)
def create_user(user: UserBase, db: Session = Depends(database.get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="User already exists")
    
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.put("/users/{user_id}", response_model=UserSchema)
def update_user(user_id: int, user: UserBase, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    email_exists = db.query(models.User).filter(models.User.email == user.email).first()
    if email_exists:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    for key, value in user.dict().items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}
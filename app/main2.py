from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, EmailStr
from datetime import datetime

from . import database, models2

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

# Pydantic models for request and response
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str  # Add password field for signup
    department_id: int
    role: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str  # Add password field for login

class UserResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    department_id: int
    role: str
    created_at: datetime

    class Config:
        from_attributes = True  # Equivalent to orm_mode in Pydantic V2

# Helper function to hash passwords (for security)
def hash_password(password: str) -> str:
    # In a real application, use a library like `bcrypt` or `passlib`
    return f"hashed_{password}"  # Placeholder for demonstration

# Helper function to verify passwords
def verify_password(plain_password: str, hashed_password: str) -> bool:
    # In a real application, use a library like `bcrypt` or `passlib`
    return f"hashed_{plain_password}" == hashed_password  # Placeholder for demonstration

# Signup endpoint
@app.post("/signup/", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(database.get_db)):
    # Check if the email is already registered
    db_user = db.query(models2.User).filter(models2.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Hash the password
    hashed_password = hash_password(user.password)

    # Create a new user
    new_user = models2.User(
        name=user.name,
        email=user.email,
        password=hashed_password,  # Store the hashed password
        department_id=user.department_id,
        role=user.role,
        created_at=datetime.utcnow(),
    )

    # Add the user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Return the user without the password
    return new_user

# Login endpoint
@app.post("/login/")
def login(user: UserLogin, db: Session = Depends(database.get_db)):
    # Find the user by email
    db_user = db.query(models2.User).filter(models2.User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Verify the password
    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    # Return a success message (or a token in a real application)
    return {"message": "Login successful", "user_id": db_user.user_id}

# API Endpoints
@app.get("/departments/", response_model=List[DepartmentSchema])
def get_departments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db)
):
    departments = db.query(models2.Department).offset(skip).limit(limit).all()
    return departments

@app.get("/departments/{department_id}", response_model=DepartmentSchema)
def get_department(department_id: int, db: Session = Depends(database.get_db)):
    department = db.query(models2.Department).filter(models2.Department.department_id == department_id).first()
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    return department

@app.get("/skills/", response_model=List[SkillSchema])
def get_skills(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db)
):
    skills = db.query(models2.Skill).offset(skip).limit(limit).all()
    return skills

@app.get("/skills/{skill_id}", response_model=SkillSchema)
def get_skill(skill_id: int, db: Session = Depends(database.get_db)):
    skill = db.query(models2.Skill).filter(models2.Skill.skill_id == skill_id).first()
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill

@app.get("/talents/", response_model=List[TalentSchema])
def get_talents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db)
):
    talents = db.query(models2.Talent).offset(skip).limit(limit).all()
    return talents

@app.get("/talents/{talent_id}", response_model=TalentSchema)
def get_talent(talent_id: int, db: Session = Depends(database.get_db)):
    talent = db.query(models2.Talent).filter(models2.Talent.talent_id == talent_id).first()
    if talent is None:
        raise HTTPException(status_code=404, detail="Talent not found")
    return talent

@app.get("/projects/", response_model=List[ProjectSchema])
def get_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db)
):
    projects = db.query(models2.Project).offset(skip).limit(limit).all()
    return projects

@app.get("/projects/{project_id}", response_model=ProjectSchema)
def get_project(project_id: int, db: Session = Depends(database.get_db)):
    project = db.query(models2.Project).filter(models2.Project.project_id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.get("/users/", response_model=List[UserSchema])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db)
):
    users = db.query(models2.User).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=UserSchema)
def get_user(user_id: int, db: Session = Depends(database.get_db)):
    user = db.query(models2.User).filter(models2.User.user_id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Project
from ..schemas.project import ProjectBase, ProjectResponse

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("/", response_model=List[ProjectResponse])
def get_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Project).offset(skip).limit(limit).all()

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("/", response_model=ProjectResponse)
def create_project(project: ProjectBase, db: Session = Depends(get_db)):
    # if db.query(Project).filter(Project.name == project.name).first():
    #     raise HTTPException(status_code=400, detail="Project already exists")
    
    new_project = Project(**project.dict())
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, project: ProjectBase, db: Session = Depends(get_db)):
    db_project = db.query(Project).filter(Project.project_id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # ✅ Debug: Print received data
    print("Received PUT Request Data:", project.dict())

    try:
        # ✅ Only update fields that are present in the request
        for key, value in project.dict(exclude_unset=True).items():
            setattr(db_project, key, value)

        db.commit()
        db.refresh(db_project)
        return db_project

    except Exception as e:
        print("Error updating project:", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}

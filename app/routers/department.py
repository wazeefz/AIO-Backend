from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.department import Department
from ..schemas.department import DepartmentResponse, DepartmentBase

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.get("/", response_model=List[DepartmentResponse])
def get_departments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Department).offset(skip).limit(limit).all()

@router.get("/{department_id}", response_model=DepartmentResponse)
def get_department(department_id: int, db: Session = Depends(get_db)):
    department = db.query(Department).filter(Department.department_id == department_id).first()
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    return department

@router.post("/", response_model=DepartmentResponse)
def create_department(department: DepartmentBase, db: Session = Depends(get_db)):
    if db.query(Department).filter(Department.department_name == department.department_name).first():
        raise HTTPException(status_code=400, detail="Department already exists")
    
    new_department = Department(**department.dict())
    db.add(new_department)
    db.commit()
    db.refresh(new_department)
    return new_department

@router.put("/{department_id}", response_model=DepartmentResponse)
def update_department(department_id: int, department: DepartmentBase, db: Session = Depends(get_db)):
    db_department = db.query(Department).filter(Department.department_id == department_id).first()
    if db_department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    
    department_exists = db.query(Department).filter(Department.department_name == department.department_name).first()
    if department_exists:
        raise HTTPException(status_code=400, detail="Department name already exists")
    
    for key, value in department.dict().items():
        setattr(db_department, key, value)

    db.commit()
    db.refresh(db_department)
    return db_department

@router.delete("/{department_id}")
def delete_department(department_id: int, db: Session = Depends(get_db)):
    department = db.query(Department).filter(Department.department_id == department_id).first()
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    
    db.delete(department)
    db.commit()
    return {"message": "Department deleted successfully"}

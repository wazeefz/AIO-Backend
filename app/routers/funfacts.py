from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.funfacts import FunFact
from ..schemas.funfacts import FunFactBase, FunFactResponse

router = APIRouter(prefix="/funfacts", tags=["funfacts"])

@router.get("/", response_model=List[FunFactResponse])
def get_funfacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(FunFact).offset(skip).limit(limit).all()

@router.get("/{fun_id}", response_model=FunFactResponse)
def get_funfact(fun_id: int, db: Session = Depends(get_db)):
    funfact = db.query(FunFact).filter(FunFact.fun_id == fun_id).first()
    if funfact is None:
        raise HTTPException(status_code=404, detail="FunFact not found")
    return funfact

@router.post("/", response_model=FunFactResponse)
def create_funfact(funfact: FunFactBase, db: Session = Depends(get_db)):
    if db.query(FunFact).filter(FunFact.fun_text == funfact.fun_text).first():
        raise HTTPException(status_code=400, detail="FunFact already exists")
    
    new_funfact = FunFact(**funfact.dict())
    db.add(new_funfact)
    db.commit()
    db.refresh(new_funfact)
    return new_funfact

@router.put("/{fun_id}", response_model=FunFactResponse)
def update_funfact(fun_id: int, funfact: FunFactBase, db: Session = Depends(get_db)):
    db_funfact = db.query(FunFact).filter(FunFact.fun_id == fun_id).first()
    if db_funfact is None:
        raise HTTPException(status_code=404, detail="FunFact not found")
    
    funfact_exists = db.query(FunFact).filter(FunFact.fun_text == funfact.fun_text).first()
    if funfact_exists:
        raise HTTPException(status_code=400, detail="FunFact already exists")
    
    for key, value in funfact.dict().items():
        setattr(db_funfact, key, value)

    db.commit()
    db.refresh(db_funfact)
    return db_funfact

@router.delete("/{fun_id}")
def delete_funfact(fun_id: int, db: Session = Depends(get_db)):
    funfact = db.query(FunFact).filter(FunFact.fun_id == fun_id).first()
    if funfact is None:
        raise HTTPException(status_code=404, detail="FunFact not found")
    
    db.delete(funfact)
    db.commit()
    return {"message": "FunFact deleted successfully"}

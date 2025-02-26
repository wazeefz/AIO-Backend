from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db 
from ..models.funfacts import FunFacts
from ..schemas.funfacts import FunFactBase, FunFactResponse

router = APIRouter(prefix="/funfacts", tags=["funfacts"])

@router.get("/", response_model=List[FunFactResponse])
def get_fun(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(FunFacts).offset(skip).limit(limit).all()

@router.get("/{fun_id}", response_model=FunFactResponse)
def get_fun(fun_id: int, db: Session = Depends(get_db)):
    fun = db.query(FunFacts).filter(FunFacts.fun_id == fun_id).first()
    if fun is None:
        raise HTTPException(status_code=404, detail="Fun Fact not found")
    return fun

@router.post("/", response_model=FunFactResponse, status_code=status.HTTP_201_CREATED)
def create_fun(chat: FunFactBase, db: Session = Depends(get_db)):
    if db.query(FunFacts).filter(FunFacts.fun_id == FunFacts.fun_id).first():
        raise HTTPException(status_code=400, detail="Fun Fact already exists")
    
    new_funfact = FunFacts(**chat.dict())
    db.add(new_funfact)
    db.commit()
    db.refresh(new_funfact)
    return new_funfact

@router.put("/{fun_id}", response_model=FunFactResponse)
def update_fun(fun_id: int, funfacts: FunFactBase, db: Session = Depends(get_db)):
    db_funfacts = db.query(FunFacts).filter(FunFacts.fun_id == fun_id).first()
    if db_funfacts is None:
        raise HTTPException(status_code=404, detail="Fun fact not found")

    for key, value in funfacts.dict(exclude_unset=True).items():  # Use exclude_unset=True
        setattr(db_funfacts, key, value)

    db.commit()
    db.refresh(db_funfacts)
    return db_funfacts

@router.delete("/{fun_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fun(fun_id: int, db: Session = Depends(get_db)):
    fun = db.query(FunFacts).filter(FunFacts.fun_id == fun_id).first()
    if fun is None:
        raise HTTPException(status_code=404, detail="Fun fact not found")
    
    db.delete(fun)
    db.commit()
    return  # No content returned on successful delete
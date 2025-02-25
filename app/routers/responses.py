from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.responses import Responses
from ..schemas.responses import ResponseBase, ResponseResponse, ResponseCreate, ResponseUpdate

router = APIRouter(prefix="/responses", tags=["responses"])

@router.get("/", response_model=List[ResponseResponse])
def get_responses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Responses).offset(skip).limit(limit).all()

@router.get("/{response_id}", response_model=ResponseResponse)
def get_response(response_id: int, db: Session = Depends(get_db)):
    response = db.query(Responses).filter(Responses.response_id == response_id).first()
    if response is None:
        raise HTTPException(status_code=404, detail="Response not found")
    return response

@router.post("/", response_model=ResponseResponse)
def create_response(response: ResponseBase, db: Session = Depends(get_db)):
    if db.query(Responses).filter(Responses.response_text == response.response_text).first():
        raise HTTPException(status_code=400, detail="Response already exists")
    
    new_response = Responses(**response.dict())
    db.add(new_response)
    db.commit()
    db.refresh(new_response)
    return new_response

@router.put("/{response_id}", response_model=ResponseResponse)
def update_response(response_id: int, response: ResponseBase, db: Session = Depends(get_db)):
    db_response = db.query(Responses).filter(Responses.response_id == response_id).first()
    if db_response is None:
        raise HTTPException(status_code=404, detail="Response not found")
    
    response_exists = db.query(Responses).filter(Responses.response_text == response.response_text).first()
    if response_exists:
        raise HTTPException(status_code=400, detail="Response text already exists")
    
    for key, value in response.dict().items():
        setattr(db_response, key, value)

    db.commit()
    db.refresh(db_response)
    return db_response

@router.delete("/{response_id}")
def delete_response(response_id: int, db: Session = Depends(get_db)):
    response = db.query(Responses).filter(Responses.response_id == response_id).first()
    if response is None:
        raise HTTPException(status_code=404, detail="Response not found")
    
    db.delete(response)
    db.commit()
    return {"message": "Response deleted successfully"}
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db  # Or wherever your database dependency is
from ..models.responses import Response
from ..schemas.responses import ResponseBase, ResponseResponse

router = APIRouter(prefix="/responses", tags=["responses"])

@router.get("/", response_model=List[ResponseResponse])
def get_educations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Response).offset(skip).limit(limit).all()

@router.get("/{response_id}", response_model=ResponseResponse)
def get_response(response_id: int, db: Session = Depends(get_db)):
    response = db.query(Response).filter(Response.response_id == response_id).first()
    if response is None:
        raise HTTPException(status_code=404, detail="Response entry not found")
    return response

@router.post("/", response_model=ResponseResponse, status_code=status.HTTP_201_CREATED)
def create_response(response_id: ResponseBase, db: Session = Depends(get_db)):
    new_response = Response(**response_id.dict())
    db.add(new_response)
    db.commit()
    db.refresh(new_response)
    return new_response

@router.put("/{response_id}", response_model=ResponseResponse)
def update_response(response_id: int, response: ResponseBase, db: Session = Depends(get_db)):
    db_response = db.query(Response).filter(Response.response_id == response_id).first()
    if db_response is None:
        raise HTTPException(status_code=404, detail="Response entry not found")

    for key, value in response.dict(exclude_unset=True).items():  # Use exclude_unset=True
        setattr(db_response, key, value)

    db.commit()
    db.refresh(db_response)
    return db_response

@router.delete("/{response_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_response(response_id: int, db: Session = Depends(get_db)):
    response = db.query(Response).filter(Response.response_id == response_id).first()
    if response is None:
        raise HTTPException(status_code=404, detail="Response entry not found")
    
    db.delete(response)
    db.commit()
    return  # No content returned on successful delete
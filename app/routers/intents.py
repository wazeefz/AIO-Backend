from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db  # Or wherever your database dependency is
from ..models.intents import Intent
from ..schemas.intents import IntentsBase, IntentsResponse

router = APIRouter(prefix="/intent", tags=["intent"])


@router.get("/", response_model=List[IntentsResponse])
def get_intent(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Intent).offset(skip).limit(limit).all()

@router.get("/{intent_id}", response_model=IntentsResponse)
def get_intent(intent_id: int, db: Session = Depends(get_db)):
    intent = db.query(Intent).filter(Intent.intent_id == intent_id).first()
    if intent is None:
        raise HTTPException(status_code=404, detail="Intent entry not found")
    return intent

@router.post("/", response_model=IntentsResponse, status_code=status.HTTP_201_CREATED)
def create_intent(intent: IntentsBase, db: Session = Depends(get_db)):
    if db.query(Intent).filter(Intent.intent_name == intent.intent_name).first():
        raise HTTPException(status_code=400, detail="Intent already exists")
    
    new_intent = Intent(**intent.dict())
    db.add(new_intent)
    db.commit()
    db.refresh(new_intent)
    return new_intent

@router.put("/{intent_id}", response_model=IntentsResponse)
def update_intent(intent_id: int, intent: IntentsBase, db: Session = Depends(get_db)):
    db_intent = db.query(Intent).filter(Intent.intent_id == intent_id).first()
    if db_intent is None:
        raise HTTPException(status_code=404, detail="Intent entry not found")

    for key, value in intent.dict(exclude_unset=True).items():  # Use exclude_unset=True
        setattr(db_intent, key, value)

    db.commit()
    db.refresh(db_intent)
    return db_intent

@router.delete("/{intent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_intent(intent_id: int, db: Session = Depends(get_db)):
    intent = db.query(Intent).filter(Intent.intent_id == intent_id).first()
    if intent is None:
        raise HTTPException(status_code=404, detail="Intent entry not found")
    
    db.delete(intent)
    db.commit()
    return  # No content returned on successful delete
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.intents import Intent
from ..schemas.intents import IntentResponse, IntentBase

router = APIRouter(prefix="/intents", tags=["Intents"])

@router.get("/", response_model=List[IntentResponse])
def get_intents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Intent).offset(skip).limit(limit).all()

@router.get("/{intent_id}", response_model=IntentResponse)
def get_intent(intent_id: int, db: Session = Depends(get_db)):
    intent = db.query(Intent).filter(Intent.intent_id == intent_id).first()
    if intent is None:
        raise HTTPException(status_code=404, detail="Intent not found")
    return intent

@router.post("/", response_model=IntentResponse)
def create_intent(intent: IntentBase, db: Session = Depends(get_db)):
    if db.query(Intent).filter(Intent.intent_name == intent.intent_name).first():
        raise HTTPException(status_code=400, detail="Intent already exists")
    
    new_intent = Intent(**intent.dict())
    db.add(new_intent)
    db.commit()
    db.refresh(new_intent)
    return new_intent

@router.put("/{intent_id}", response_model=IntentResponse)
def update_intent(intent_id: int, intent: IntentBase, db: Session = Depends(get_db)):
    db_intent = db.query(Intent).filter(Intent.intent_id == intent_id).first()
    if db_intent is None:
        raise HTTPException(status_code=404, detail="Intent not found")
    
    intent_exists = db.query(Intent).filter(Intent.intent_name == intent.intent_name).first()
    if intent_exists:
        raise HTTPException(status_code=400, detail="Intent name already exists")
    
    for key, value in intent.dict().items():
        setattr(db_intent, key, value)

    db.commit()
    db.refresh(db_intent)
    return db_intent

@router.delete("/{intent_id}")
def delete_intent(intent_id: int, db: Session = Depends(get_db)):
    intent = db.query(Intent).filter(Intent.intent_id == intent_id).first()
    if intent is None:
        raise HTTPException(status_code=404, detail="Intent not found")
    
    db.delete(intent)
    db.commit()
    return {"message": "Intent deleted successfully"}

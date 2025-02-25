from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.feedback import Feedback
from ..schemas.feedback import FeedbackResponse, FeedbackBase

router = APIRouter(prefix="/feedback", tags=["Feedback"])

@router.get("/", response_model=List[FeedbackResponse])
def get_feedback(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Feedback).offset(skip).limit(limit).all()

@router.get("/{feedback_id}", response_model=FeedbackResponse)
def get_feedback(feedback_id: int, db: Session = Depends(get_db)):
    feedback = db.query(Feedback).filter(Feedback.feedback_id == feedback_id).first()
    if feedback is None:
        raise HTTPException(status_code=404, detail="Feedabck not found")
    return feedback

@router.post("/", response_model=FeedbackResponse)
def create_feedback(feedback: FeedbackBase, db: Session = Depends(get_db)):
    if db.query(Feedback).filter(Feedback.name == feedback.name).first():
        raise HTTPException(status_code=400, detail="Feedaback already exists")
    
    new_feedback = Feedback(**Feedback.dict())
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    return new_feedback

@router.put("/{feedback_id}", response_model=FeedbackResponse)
def update_feedback(feedback_id: int, feedback: FeedbackBase, db: Session = Depends(get_db)):
    db_feedback = db.query(Feedback).filter(Feedback.feedback_id == feedback_id).first()
    if db_feedback is None:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    feedback_exists = db.query(Feedback).filter(Feedback.feedback_name == feedback.feedback_name).first()
    if feedback_exists:
        raise HTTPException(status_code=400, detail="Feedback name already exists")
    
    for key, value in feedback.dict().items():
        setattr(db_feedback, key, value)

    db.commit()
    db.refresh(db_feedback)
    return db_feedback

@router.delete("/{feedback_id}")
def delete_feedback(feedback_id: int, db: Session = Depends(get_db)):
    feedback = db.query(Feedback).filter(Feedback.feedback_id == feedback_id).first()
    if feedback is None:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    db.delete(feedback)
    db.commit()
    return {"message": "Feedback deleted successfully"}

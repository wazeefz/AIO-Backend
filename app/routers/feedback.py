from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Feedback
from ..schemas.feedback import FeedbackBase, FeedbackResponse

router = APIRouter(prefix="/feedback", tags=["feedback"])

@router.get("/", response_model=List[FeedbackResponse])
def get_feedback(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Feedback).offset(skip).limit(limit).all()

@router.get("/{feedback_id}", response_model=FeedbackResponse)
def get_feedback(feedback_id: int, db: Session = Depends(get_db)):
    feedback = db.query(Feedback).filter(Feedback.feedback_id == feedback_id).first()
    if feedback is None:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback

@router.post("/", response_model=FeedbackResponse)
def create_feedback(feedback: FeedbackBase, db: Session = Depends(get_db)):
    new_feedback = Feedback(**feedback.dict())
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    return new_feedback

@router.put("/{feedback_id}", response_model=FeedbackResponse)
def update_feedback(feedback_id: int, feedback: FeedbackBase, db: Session = Depends(get_db)):
    db_feedback = db.query(Feedback).filter(Feedback.feedback_id == feedback_id).first()
    if db_feedback is None:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
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

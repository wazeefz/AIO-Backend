from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.messages import Messages
from ..schemas.messages import MessagesBase, MessagesResponse, MessagesCreate, MessagesUpdate

router = APIRouter(prefix="/messages", tags=["messages"])

@router.get("/", response_model=List[MessagesResponse])
def get_messages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Messages).offset(skip).limit(limit).all()

@router.get("/{message_id}", response_model=MessagesResponse)
def get_message(message_id: int, db: Session = Depends(get_db)):
    message = db.query(Messages).filter(Messages.message_id == message_id).first()
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return message

@router.post("/", response_model=MessagesResponse)
def create_message(message: MessagesBase, db: Session = Depends(get_db)):
    if db.query(Messages).filter(Messages.sender == message.sender).first():
        raise HTTPException(status_code=400, detail="Message already exists")
    
    new_message = Messages(**message.dict())
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

@router.put("/{message_id}", response_model=MessagesResponse)
def update_message(message_id: int, message: MessagesBase, db: Session = Depends(get_db)):
    db_message = db.query(Messages).filter(Messages.message_id == message_id).first()
    if db_message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    
    message_exists = db.query(Messages).filter(Messages.sender == message.sender).first()
    if message_exists:
        raise HTTPException(status_code=400, detail="Message sender already exists")
    
    for key, value in message.dict().items():
        setattr(db_message, key, value)

    db.commit()
    db.refresh(db_message)
    return db_message

@router.delete("/{message_id}")
def delete_message(message_id: int, db: Session = Depends(get_db)):
    message = db.query(Messages).filter(Messages.message_id == message_id).first()
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    
    db.delete(message)
    db.commit()
    return {"message": "Message deleted successfully"}
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db  # Or wherever your database dependency is
from ..models.messages import Messages
from ..schemas.messages import MessagesBase, MessagesResponse

router = APIRouter(prefix="/messages", tags=["messages"])


@router.get("/", response_model=List[MessagesBase])
def get_message(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Messages).offset(skip).limit(limit).all()

@router.get("/{message_id}", response_model=MessagesResponse)
def get_message(message_id: int, db: Session = Depends(get_db)):
    message = db.query(Messages).filter(Messages.message_id == message_id).first()
    if message is None:
        raise HTTPException(status_code=404, detail="Messages entry not found")
    return message

@router.post("/", response_model=MessagesResponse, status_code=status.HTTP_201_CREATED)
def create_message(messages: MessagesBase, db: Session = Depends(get_db)):
    if db.query(Messages).filter(Messages.sender == messages.sender).first():
        raise HTTPException(status_code=400, detail="Messages already exists")
    
    new_message = Messages(**messages.dict())
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

@router.put("/{conversation_id}", response_model=MessagesResponse)
def update_message(conversation_id: int, messages: MessagesBase, db: Session = Depends(get_db)):
    db_message = db.query(Messages).filter(Messages.conversation_id == conversation_id).first()
    if db_message is None:
        raise HTTPException(status_code=404, detail="Message entry not found")

    for key, value in messages.dict(exclude_unset=True).items():  # Use exclude_unset=True
        setattr(db_message, key, value)

    db.commit()
    db.refresh(db_message)
    return db_message

@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(conversation_id: int, db: Session = Depends(get_db)):
    message = db.query(Messages).filter(Messages.conversation_id == conversation_id).first()
    if message is None:
        raise HTTPException(status_code=404, detail="Messages entry not found")
    
    db.delete(message)
    db.commit()
    return  # No content returned on successful delete
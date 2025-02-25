from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db 
from ..models.chat import Chat
from ..schemas.chat import ChatBase, ChatResponse

router = APIRouter(prefix="/chats", tags=["chats"])

@router.get("/", response_model=List[ChatResponse])
def get_chats(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Chat).offset(skip).limit(limit).all()

@router.get("/{conversation_id}", response_model=ChatResponse)
def get_chat(conversation_id: int, db: Session = Depends(get_db)):
    chat = db.query(Chat).filter(Chat.conversation_id == conversation_id).first()
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

@router.post("/", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
def create_chat(chat: ChatBase, db: Session = Depends(get_db)):
    if db.query(Chat).filter(Chat.name == chat.name).first():
        raise HTTPException(status_code=400, detail="Chat already exists")
    
    new_chat = Chat(**chat.dict())
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return new_chat

@router.put("/{conversation_id}", response_model=ChatResponse)
def update_chat(conversation_id: int, chat: ChatBase, db: Session = Depends(get_db)):
    db_chat = db.query(Chat).filter(Chat.conversation_id == conversation_id).first()
    if db_chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")

    for key, value in chat.dict(exclude_unset=True).items():  # Use exclude_unset=True
        setattr(db_chat, key, value)

    db.commit()
    db.refresh(db_chat)
    return db_chat

@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat(conversation_id: int, db: Session = Depends(get_db)):
    chat = db.query(Chat).filter(Chat.conversation_id == conversation_id).first()
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    db.delete(chat)
    db.commit()
    return  # No content returned on successful delete
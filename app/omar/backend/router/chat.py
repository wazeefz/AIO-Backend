from . import database, schemas 
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db.db_connection import get_db

router = APIRouter()

# Chat Endpoints
@router.post("/chat/{user_id}", response_model=schemas.ChatResponse)
async def create_chat(
    user_id: int,
    db: Session = Depends(database.get_db)
):
    new_chat = Chat(user_id=user_id, title="New Chat")
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return new_chat

@router.get("/chat/{user_id}/{chat_id}", response_model=schemas.ChatResponse)
async def get_chat(
    user_id: int,
    chat_id: int,
    db: Session = Depends(database.get_db)
):
    chat = db.query(Chat).filter(
        Chat.conversation_id == chat_id,
        Chat.user_id == user_id
    ).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

@router.get("/chat/history/{user_id}", response_model=List[schemas.ChatResponse])
async def get_chat_history(
    user_id: int,
    db: Session = Depends(database.get_db)
):
    chats = db.query(Chat).filter(
        Chat.user_id == user_id
    ).order_by(Chat.updated_at.desc()).all()
    return chats

@router.delete("/chat/{user_id}/{chat_id}", response_model=schemas.ChatResponse)
async def delete_chat(
    user_id: int,
    chat_id: int,
    db: Session = Depends(database.get_db)
):
    chat = db.query(Chat).filter(
        Chat.conversation_id == chat_id,
        Chat.user_id == user_id
    ).first()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    db.delete(chat)
    db.commit()
    return {"message": "Chat deleted successfully"}
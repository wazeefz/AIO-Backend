from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.chat import Chat, Message
from ..schemas.chat import ChatResponse, ChatListResponse, MessageResponse, MessageCreate   

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/", response_model=ChatResponse)
async def create_chat(user_id: int, db: Session = Depends(get_db)):
    new_chat = Chat(user_id=user_id, title="New Chat")
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return new_chat

@router.get("/", response_model=ChatResponse)
async def get_chat(user_id: int, chat_id: int, db: Session = Depends(get_db)):
    chat = db.query(Chat).filter(Chat.conversation_id == chat_id, Chat.user_id == user_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

@router.get("/", response_model=List[ChatListResponse])
def get_user_chats(user_id: int, db: Session = Depends(get_db)):
    try:
        chats = db.query(Chat).filter(Chat.user_id == user_id).order_by(Chat.updated_at.desc()).all()
        if not chats:
            return []
        return chats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[MessageResponse])
async def get_chat_messages(user_id: int, chat_id: int, db: Session = Depends(get_db)):
    try:
        chat = db.query(Chat).filter(Chat.conversation_id == chat_id, Chat.user_id == user_id).first()
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        messages = db.query(Message).filter(Message.conversation_id == chat_id).order_by(Message.created_at).all()
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=MessageResponse)
async def create_message(user_id: int, chat_id: int, message: MessageCreate, db: Session = Depends(get_db)):
    chat = db.query(Chat).filter(Chat.conversation_id == chat_id, Chat.user_id == user_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    new_message = Message(
        conversation_id=chat_id,
        content=message.content,
        role=message.role
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message



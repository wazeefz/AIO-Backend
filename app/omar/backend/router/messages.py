from . import database, schemas 
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db.db_connection import get_db

router = APIRouter()

@router.post("/chat/{user_id}/{chat_id}/message", response_model=schemas.MessageResponse)
async def create_message(
    user_id: int,
    chat_id: int,
    message: schemas.MessageCreate,
    db: Session = Depends(database.get_db)
):
    chat = db.query(Chat).filter(
        Chat.conversation_id == chat_id,
        Chat.user_id == user_id
    ).first()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    new_message = Message(
        conversation_id=chat_id,
        content=message.content,
        role=message.role
    )
    db.add(new_message)

    if message.role == "user" and len(chat.messages) == 0:
        chat.title = message.content[:30] + "..." if len(message.content) > 30 else message.content

    chat.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(new_message)
    return new_message
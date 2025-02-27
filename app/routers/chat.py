import os
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain.chains import RetrievalQA
from datetime import datetime
from ..database import get_db
from ..models.chat import Chat, Message
from ..schemas.chat import ChatResponse, ChatListResponse, MessageResponse, MessageCreate   

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize Google Generative AI model and embeddings
llm_model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=GOOGLE_API_KEY)



router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/{user_id}", response_model=ChatResponse)
def create_chat(user_id: int, db: Session = Depends(get_db)):
    new_chat = Chat(user_id=user_id, title="New Chat")
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return new_chat

@router.get("/{user_id}/{chat_id}", response_model=ChatResponse)
async def get_chat(user_id: int, chat_id: int, db: Session = Depends(get_db)):
    chat = db.query(Chat).filter(Chat.conversation_id == chat_id, Chat.user_id == user_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

@router.get("/{user_id}", response_model=List[ChatListResponse])
def get_user_chats(user_id: int, db: Session = Depends(get_db)):
    try:
        chats = db.query(Chat).filter(Chat.user_id == user_id)#.order_by(Chat.updated_at.desc()).all()
        if not chats:
            return []
        return chats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/{chat_id}/messages", response_model=List[MessageResponse])
async def get_chat_messages(user_id: int, chat_id: int, db: Session = Depends(get_db)):
    try:
        chat = db.query(Chat).filter(Chat.conversation_id == chat_id, Chat.user_id == user_id).first()
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        messages = db.query(Message).filter(Message.conversation_id == chat_id).order_by(Message.created_at).all()
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{user_id}/{chat_id}/message", response_model=MessageResponse)
async def create_message(
    user_id: int, 
    chat_id: int, 
    message: MessageCreate, 
    db: Session = Depends(get_db)
):
    # Print received data for debugging
    print(f"Received message data: {message.dict()}")
    
    chat = db.query(Chat).filter(
        Chat.conversation_id == chat_id, 
        Chat.user_id == user_id
    ).first()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
        
    new_message = Message(
        conversation_id=chat_id,
        message_text=message.message_text,
        sender=message.sender
    )
    
    try:
        db.add(new_message)
        if message.sender == "user" and len(chat.messages) == 0:
            chat.title = (
                message.message_text[:30] + "..." 
                if len(message.message_text) > 30 
                else message.message_text
            )
        
        db.commit()
        db.refresh(new_message)
        return new_message
    except Exception as e:
        print(f"Error creating message: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ask-question/")
async def ask_question(question: str = Query(..., description="Your question")):
    try:
        response = llm_model.invoke(question)
        return {
            "content": response.content if hasattr(response, 'content') else str(response)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/{user_id}/{chat_id}", )
async def delete_chat(
    user_id: int,
    chat_id: int,
    db: Session = Depends(get_db)
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
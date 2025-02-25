from pydantic import BaseModel
from typing import List
from datetime import datetime

class MessageCreate(BaseModel):
    content: str
    role: str

class MessageResponse(BaseModel):
    message_id: int
    content: str
    role: str
    created_at: datetime

    class Config:
        orm_mode = True

class ChatResponse(BaseModel):
    conversation_id: int
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse]

    class Config:
        orm_mode = True

class ChatListResponse(BaseModel):
    conversation_id: int
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


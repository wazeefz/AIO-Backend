from pydantic import BaseModel
from typing import List
from datetime import datetime

class MessageCreate(BaseModel):
    message_text: str
    # content: str
    sender: str
    # role: str

class MessageResponse(BaseModel):
    message_id: int
    message_text: str
    sender: str
    # content: str
    # role: str
    created_at: datetime

    class Config:
        orm_mode = True

class ChatResponse(BaseModel):
    conversation_id: int
    title: str
    started_at: datetime
    # created_at: datetime
    # updated_at: datetime
    messages: List[MessageResponse]

    class Config:
        orm_mode = True

class ChatListResponse(BaseModel):
    conversation_id: int
    title: str
    started_at: datetime
    # created_at: datetime
    # updated_at: datetime

    class Config:
        orm_mode = True


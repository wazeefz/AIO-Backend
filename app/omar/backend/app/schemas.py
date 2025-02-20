from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta

# Pydantic model for user signup
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    department_id: Optional[int] = None
    role: Optional[str] = "user"

# Pydantic models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_name: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    department_id: Optional[int] = None
    role: Optional[str] = None

class DepartmentResponse(BaseModel):
    department_id: int
    department_name: str

    class Config:
        orm_mode = True

class UserResponse(BaseModel):
    user_id: int
    name: str
    email: str
    department_id: Optional[int]
    role: Optional[str]
    department: Optional[DepartmentResponse]
    created_at: datetime

    class Config:
        orm_mode = True

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
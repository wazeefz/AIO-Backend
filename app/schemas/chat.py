from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Base Schema - Shared attributes
class ChatBase(BaseModel):
    conversation_id: int
    user_id: int
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    project_id: Optional[int] = None

# Create Schema - Used for input validation when creating a new chat
class ChatCreate(ChatBase):
    conversation_id : int 

# Update Schema - Used when updating an existing chat
class ChatUpdate(ChatBase):
    pass  # All fields are optional

# Response Schema - Includes conversation_id (read-only)
class ChatResponse(ChatBase):  # Renamed to Chat for clarity
    user_id: int

    class Config:
        from_attributes = True  # Ensures compatibility with ORM models


# Schema for a list of Chat objects (important for GET requests returning multiple chats)
# class ChatList(BaseModel):
#     chats: List[ChatResponse]
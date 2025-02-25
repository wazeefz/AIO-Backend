from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Base Schema - Shared attributes
class MessagesBase(BaseModel):
    conversation_id: int
    sender: str
    created_at: Optional[datetime] = None
    edited_at: Optional[datetime] = None
    intent_id: Optional[int] = None
    response_id: Optional[int] = None
    project_id: Optional[int] = None
    suggested_team_json: Optional[str] = None

# Create Schema - Used for input validation when creating a new message
class MessagesCreate(MessagesBase):
    sender: str  # Required field

# Update Schema - Used when updating an existing message
class MessagesUpdate(MessagesBase):
    pass  # All fields are optional

# Response Schema - Includes ID (read-only)
class MessagesResponse(MessagesBase):
    message_id: int

    class Config:
        from_attributes = True  # Ensures compatibility with ORM models
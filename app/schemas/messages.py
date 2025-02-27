from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class MessagesBase(BaseModel):
    message_id: int
    conversation_id: int
    sender: str
    message_text: str
    created_at: Optional[datetime]
    edited_at: Optional[datetime]
    intent_id: Optional[int] = None
    response_id: Optional[int]
    project_id: Optional[int]
    suggested_team_json: Optional[dict] 


class MessagesCreate(MessagesBase):
    intent_id: int
    

class MessagesUpdate(MessagesBase):
    pass  # All fields optional for updates

class MessagesResponse(MessagesBase):  # Response schema
    message_id: int

    class Config:
        from_attributes = True

# class EducationList(BaseModel):  # For returning lists of Education
#     educations: List[Education]
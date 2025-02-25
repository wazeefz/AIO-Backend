from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Base Schema - Shared attributes
class FeedbackBase(BaseModel):

    feedback_id: Optional[int] = None
    message_id: Optional[int] = None
    rating: Optional[int] = None
    created_at: Optional[datetime] = None
    feedback_text: Optional[str] = None

# Create Schema - Used for input validation when creating a new project
class FeedbackCreate(FeedbackBase):
    id: int  # Required field

# Update Schema - Used when updating an existing project
class FeedbackUpdate(FeedbackBase):
    pass  # All fields are optional

# Response Schema - Includes ID (read-only)
class FeedbackResponse(FeedbackBase):
    feedback_id: int

    class Config:
        from_attributes = True  # Ensures compatibility with ORM models

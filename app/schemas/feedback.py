from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Base Schema - Shared attributes
class FeedbackBase(BaseModel):
    rating: int
    created_at: datetime
    feedback_text: str

# Create Schema - Used for input validation when creating a new feedback
# class FeedbackCreate(FeedbackBase):
#     message_id: int

# Update Schema - Used when updating an existing feedback
class FeedbackUpdate(FeedbackBase):
    pass  # All fields are optional

# Response Schema - Includes ID (read-only)
class FeedbackResponse(FeedbackBase):
    feedback_id: int

    class Config:
        from_attributes = True  # Ensures compatibility with ORM models
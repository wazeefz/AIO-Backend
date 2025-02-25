from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Base Schema - Shared attributes
class IntentBase(BaseModel):

    intent_id: Optional[int] = None
    intent_name: Optional[str] = None
    description: Optional[str] = None

# Create Schema - Used for input validation when creating a new project
class IntentCreate(IntentBase):
    id: int  # Required field

# Update Schema - Used when updating an existing project
class IntentUpdate(IntentBase):
    pass  # All fields are optional

# Response Schema - Includes ID (read-only)
class IntentResponse(IntentBase):
    intent_id: int

    class Config:
        from_attributes = True  # Ensures compatibility with ORM models
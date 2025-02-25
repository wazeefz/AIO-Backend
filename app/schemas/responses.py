from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Base Schema - Shared attributes
class ResponseBase(BaseModel):
    response_text: str
    response_template: Optional[str] = None

# Create Schema - Used for input validation when creating a new response
class ResponseCreate(ResponseBase):
    response_text: str  # Required field

# Update Schema - Used when updating an existing response
class ResponseUpdate(ResponseBase):
    pass  # All fields are optional

# Response Schema - Includes ID (read-only)
class ResponseResponse(ResponseBase):
    response_id: int

    class Config:
        from_attributes = True  # Ensures compatibility with ORM models
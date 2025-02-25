from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Base Schema - Shared attributes
class FunFactBase(BaseModel):
    fun_id: int
    fun_text: str
    fact_type: str
    relevance_score: int

# Create Schema - Used for input validation when creating a new funfact
class FunFactCreate(FunFactBase):
    fun_text: str  # Required field
    fact_type: str  # Required field
    relevance_score: int  # Required field

# Update Schema - Used when updating an existing funfact
class FunFactUpdate(FunFactBase):
    pass  # All fields are optional

# Response Schema - Includes ID (read-only)
class FunFactResponse(FunFactBase):
    fun_id: int

    class Config:
        from_attributes = True  # Ensures compatibility with ORM models
        

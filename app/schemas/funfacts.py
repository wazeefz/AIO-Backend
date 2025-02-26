from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Base Schema - Shared attributes
class FunFactBase(BaseModel):
    project_id: int
    talent_id: int
    fun_text: str
    fact_type: str
    relevance_score: int

# Create Schema - Used for input validation when creating a new chat
# class FunFactCreate(FunFactBase):
#     fun_id: int

# Update Schema - Used when updating an existing chat
class FunFactUpdate(FunFactBase):
    pass


class FunFactResponse(FunFactBase):
    fun_id: int

    class Config:
        from_attributes = True

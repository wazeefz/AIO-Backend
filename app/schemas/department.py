from pydantic import BaseModel
from typing import List, Optional

# Base Schema - Shared attributes
class DepartmentBase(BaseModel):
    department_name: str

# Response Schema - Includes ID (read-only)
class DepartmentResponse(DepartmentBase):
    department_id: int

    class Config:
        from_attributes = True  # Ensures compatibility with ORM models
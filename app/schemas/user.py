from pydantic import BaseModel
from typing import Optional

# Base Schema - Shared attributes
class UserBase(BaseModel):
    name: str
    email: str  # Ensures valid email format
    department_id: Optional[int] = None
    role: Optional[str] = None

# Create Schema - Used for input validation when creating a new user
class UserCreate(UserBase):
    name: str  # Required field
    email: str  # Required field

# Update Schema - Used when updating an existing user
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    department_id: Optional[int] = None
    role: Optional[str] = None

# Response Schema - Includes ID (read-only)
class UserResponse(UserBase):
    user_id: int

    class Config:
        from_attributes = True  # Ensures compatibility with ORM models

# New Schema for Signup (Same as UserCreate)
class UserSignup(UserBase):
    pass  # No changes needed, inherits all fields

# New Schema for Login (Only email required)
class UserLogin(BaseModel):
    email: str  # Only email is required for login
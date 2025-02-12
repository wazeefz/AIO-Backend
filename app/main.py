from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from . import database, models

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProfileSchema(BaseModel):
    id: int
    name: str
    age: int
    email: str
    marital_status: str
    country: str
    state: str
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True

@app.get("/profiles/", response_model=List[ProfileSchema])
def get_profiles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db)
):
    profiles = db.query(models.Profile).offset(skip).limit(limit).all()
    return profiles
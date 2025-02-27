from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class ResponseBase(BaseModel):
    response_id: int
    intent_id: Optional[int]  # Make intent_id optional
    response_text: str
    response_template: Optional[Dict]  # Use Dict for JSON


class ResponseCreate(ResponseBase):
    pass


class ResponseResponse(ResponseBase):
    response_id: int

    class Config:
        from_attributes = True

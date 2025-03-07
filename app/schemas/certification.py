from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CertificationBase(BaseModel):
    talent_id: int
    certification_name: str
    issuing_organization: str
    credential_id: Optional[str] = None
    start_date: datetime
    has_expiration_date: Optional[bool] = False
    expiration_date: Optional[datetime] = None

class CertificationCreate(CertificationBase):
    pass

class CertificationUpdate(BaseModel):
    certification_name: Optional[str] = None
    issuing_organization: Optional[str] = None
    credential_id: Optional[str] = None
    start_date: Optional[datetime] = None
    has_expiration_date: Optional[bool] = None
    expiration_date: Optional[datetime] = None

class CertificationResponse(CertificationBase):
    certification_id: int

    class Config:
        from_attributes = True
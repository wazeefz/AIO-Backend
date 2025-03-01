from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Certification(Base):
    __tablename__ = "certification"

    certification_id = Column(Integer, primary_key=True, index=True)
    talent_id = Column(Integer, ForeignKey("talents.talent_id", ondelete="CASCADE"))
    certification_name = Column(String(100), nullable=False)
    issuing_organization = Column(String(100), nullable=False)
    credential_id = Column(Integer)
    start_date = Column(DateTime, nullable=False)
    has_expiration_date = Column(Boolean, default=False)
    expiration_date = Column(DateTime)

    # Relationship
    talent = relationship("Talent", back_populates="certifications")

    def to_dict(self):
        return {
            "certification_id": self.certification_id,
            "certification_name": self.certification_name,
            "issuing_organization": self.issuing_organization,
            "credential_id": self.credential_id,
            "start_date": self.start_date,
            "expiration_date": self.expiration_date
        }
import uuid
from sqlalchemy import Column, String, Date, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from core.database import Base


class Citizen(Base):
    __tablename__ = "citizens"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nik = Column(String(16), unique=True, nullable=False, index=True)
    dob = Column(Date, nullable=False)
    province = Column(String(100), nullable=True)
    regency = Column(String(100), nullable=True)
    role = Column(String(20), nullable=False, default="user")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    aspirations = relationship(
        "Aspiration",
        back_populates="citizen",
        cascade="all, delete-orphan"
    )
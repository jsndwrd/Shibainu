from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, date

class CitizenBase(BaseModel):
    nik: str
    dob: date
    province: str | None = None

class CitizenResponse(CitizenBase):
    id: UUID
    created_at: datetime
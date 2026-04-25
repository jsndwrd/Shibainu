from pydantic import BaseModel, Field
from datetime import date
from uuid import UUID

class LoginRequest(BaseModel):
    nik: str = Field(min_length=16, max_length=16)
    dob: date

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    citizen_id: UUID

class MeResponse(BaseModel):
    id: UUID
    nik: str
    province: str | None
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AspirationCreate(BaseModel):
    description: str = Field(min_length=15, max_length=1000)
    category: Optional[str] = None
    province: str
    regency: str
    impact_scope: str = "Community"
    target_level: str = "DPRD"
    population: Optional[int] = Field(default=100000, ge=1)


class AspirationResponse(BaseModel):
    id: UUID
    citizen_id: UUID
    description: str
    cleaned_description: Optional[str]
    predicted_category: Optional[str]
    category_confidence: Optional[float]
    predicted_asta_cita: Optional[str]
    asta_confidence: Optional[float]
    cluster_id: Optional[UUID]
    status: str
    submitted_at: datetime

    class Config:
        from_attributes = True


class AspirationListItem(BaseModel):
    id: UUID
    predicted_category: Optional[str]
    predicted_asta_cita: Optional[str]
    cluster_id: Optional[UUID]
    status: str
    submitted_at: datetime

    class Config:
        from_attributes = True
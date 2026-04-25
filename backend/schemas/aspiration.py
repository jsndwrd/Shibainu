from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List

class AspirationCreate(BaseModel):
    description: str = Field(min_length=15, max_length=500)
    category: Optional[str] = None
    urgency: Optional[int] = Field(default=None, ge=1, le=5)
    province: str
    regency: str
    impact_scope: str
    target_level: str

class AspirationResponse(BaseModel):
    id: UUID
    citizen_id: UUID
    description: str
    cleaned_description: str
    predicted_category: str
    predicted_urgency: int
    cluster_id: UUID
    priority_score: float
    status: str
    submitted_at: datetime

class AspirationListItem(BaseModel):
    id: UUID
    category: str
    urgency: int
    cluster_id: UUID
    submitted_at: datetime
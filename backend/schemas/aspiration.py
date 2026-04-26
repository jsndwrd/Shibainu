from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional


class AspirationCreate(BaseModel):
    description: str = Field(min_length=15, max_length=500)
    category: Optional[str] = None
    province: str
    regency: str
    impact_scope: str
    target_level: str


class AspirationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    citizen_id: UUID
    description: str
    cleaned_description: Optional[str] = None

    category_user_input: Optional[str] = None
    predicted_category: Optional[str] = None
    category_confidence: Optional[float] = 0

    predicted_asta_cita: Optional[str] = None
    asta_confidence: Optional[float] = 0

    policy_level: Optional[str] = None
    policy_level_confidence: Optional[float] = 0
    policy_level_reason: Optional[str] = None
    routing_target: Optional[str] = None

    province: Optional[str] = None
    regency: Optional[str] = None
    impact_scope: Optional[str] = None
    target_level: Optional[str] = None

    cluster_id: Optional[UUID] = None
    priority_score: Optional[float] = 0

    status: str
    submitted_at: datetime


class AspirationListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    category_user_input: Optional[str] = None
    predicted_category: Optional[str] = None

    policy_level: Optional[str] = None
    policy_level_confidence: Optional[float] = 0
    routing_target: Optional[str] = None

    cluster_id: Optional[UUID] = None
    priority_score: Optional[float] = 0
    status: Optional[str] = None
    submitted_at: datetime
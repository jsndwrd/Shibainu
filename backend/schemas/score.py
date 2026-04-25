from datetime import datetime
from typing import Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PriorityScoreRequest(BaseModel):
    report_count: int = Field(..., ge=0)
    unique_regions: int = Field(..., ge=0)
    asta_cita: Optional[str] = None
    asta_confidence: Optional[float] = Field(default=None, ge=0, le=1)
    max_report_count: int = Field(default=100, ge=1)
    max_regions: int = Field(default=10, ge=1)


class PriorityScoreResponse(BaseModel):
    priority_score: float
    priority_level: str
    should_generate_brief: bool
    normalized_score: float
    components: Dict[str, float]
    weights: Dict[str, float]
    raw_inputs: Dict


class ScoreResponse(BaseModel):
    cluster_id: UUID
    volume_score: float
    spread_score: float
    asta_cita_score: float
    total_score: float
    priority_level: str
    should_generate_brief: bool
    computed_at: datetime

    class Config:
        from_attributes = True
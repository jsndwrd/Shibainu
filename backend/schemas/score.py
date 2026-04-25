from datetime import datetime
from typing import Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PriorityScoreRequest(BaseModel):
    report_count: int = Field(..., ge=0)
    population: int = Field(..., ge=1)
    unique_regions: int = Field(..., ge=0)
    asta_cita: Optional[str] = None
    asta_confidence: Optional[float] = Field(default=None, ge=0, le=1)
    max_regions: int = Field(default=10, ge=1)
    max_reports_per_100k: float = Field(default=30.0, gt=0)


class PriorityScoreResponse(BaseModel):
    priority_score: float
    priority_level: str
    should_generate_brief: bool
    normalized_score: float
    components: Dict[str, float]
    raw_metrics: Dict
    weights: Dict[str, float]


class ScoreResponse(BaseModel):
    cluster_id: UUID
    gdi_score: float
    pavi_score: float
    asta_cita_score: float
    reports_per_100k: float
    population: int
    total_score: float
    priority_level: str
    should_generate_brief: bool
    computed_at: datetime

    class Config:
        from_attributes = True
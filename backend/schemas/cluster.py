from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import List, Optional


class ClusterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    label: str
    category: str

    member_count: int = 0
    avg_urgency: float = 0.0
    top_provinces: List[str] = []

    priority_score: float = 0.0

    population: int = 0
    dominant_asta_cita: Optional[str] = None
    asta_confidence: float = 0.0

    created_at: datetime
    last_updated: datetime


class ClusterDetailResponse(ClusterResponse):
    sub_topics: List[str] = []
    urgency_dist: dict = {}
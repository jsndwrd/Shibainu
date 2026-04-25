from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class ClusterResponse(BaseModel):
    id: UUID
    label: str
    category: str
    member_count: int
    top_provinces: List[str]
    population: Optional[int]
    dominant_asta_cita: Optional[str]
    asta_confidence: Optional[float]
    created_at: datetime
    last_updated: datetime

    class Config:
        from_attributes = True


class ClusterDetailResponse(ClusterResponse):
    sub_topics: List[str]
    dominant_impact_scope: Optional[str]

    class Config:
        from_attributes = True
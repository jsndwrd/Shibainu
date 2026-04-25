from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List

class ClusterResponse(BaseModel):
    id: UUID
    label: str
    category: str
    member_count: int
    avg_urgency: float
    top_provinces: List[str]
    priority_score: float
    created_at: datetime
    last_updated: datetime

class ClusterDetailResponse(ClusterResponse):
    sub_topics: List[str]
    urgency_dist: dict
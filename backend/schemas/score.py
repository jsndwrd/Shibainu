from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class ScoreResponse(BaseModel):
    cluster_id: UUID
    volume_score: float
    urgency_score: float
    geo_score: float
    impact_score: float
    total_score: float
    computed_at: datetime
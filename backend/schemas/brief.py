from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel


class BriefGenerateRequest(BaseModel):
    cluster_ids: List[UUID]


class BriefResponse(BaseModel):
    id: UUID
    cluster_id: UUID
    content: str
    urgency_classification: str
    generated_by: str
    member_count_at_generation: int
    priority_score_at_generation: float
    generated_at: datetime

    class Config:
        from_attributes = True
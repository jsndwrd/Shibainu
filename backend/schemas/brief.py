from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List

class BriefGenerateRequest(BaseModel):
    cluster_ids: List[UUID]

class BriefResponse(BaseModel):
    id: UUID
    cluster_id: UUID
    content: str
    urgency_classification: str
    generated_by: str
    generated_at: datetime
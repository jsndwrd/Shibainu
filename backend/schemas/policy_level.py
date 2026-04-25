from typing import Optional

from pydantic import BaseModel, Field


class PolicyLevelRequest(BaseModel):
    text: str = Field(..., min_length=5)
    category: Optional[str] = None
    asta_cita: Optional[str] = None
    report_count: int = Field(default=1, ge=1)
    unique_regions: int = Field(default=1, ge=1)


class PolicyLevelResponse(BaseModel):
    policy_level: str
    routing_target: str
    confidence: float
    strategic_score: int
    operational_score: int
    reason: str
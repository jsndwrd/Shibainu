from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class MessageResponse(BaseModel):
    message: str

class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
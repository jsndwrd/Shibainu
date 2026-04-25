import uuid
from sqlalchemy import (
    Column,
    String,
    DateTime
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_id = Column(UUID(as_uuid=True), nullable=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(100), nullable=False)
    metadata = Column(JSONB, default={})
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
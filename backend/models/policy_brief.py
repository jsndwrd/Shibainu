import uuid
from sqlalchemy import (
    Column,
    Text,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from core.database import Base


class PolicyBrief(Base):
    __tablename__ = "policy_briefs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cluster_id = Column(
        UUID(as_uuid=True),
        ForeignKey("clusters.id", ondelete="CASCADE"),
        nullable=False
    )
    content = Column(Text, nullable=False)
    urgency_classification = Column(String(30), nullable=True)
    generated_by = Column(String(50), nullable=False)
    member_count_at_generation = Column(Integer, default=0)
    priority_score_at_generation = Column(Float, default=0)
    is_stale = Column(Boolean, default=False)
    generated_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    cluster = relationship(
        "Cluster",
        back_populates="briefs"
    )
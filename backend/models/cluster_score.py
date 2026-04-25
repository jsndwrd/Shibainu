import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.database import Base


class ClusterScore(Base):
    __tablename__ = "cluster_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    cluster_id = Column(
        UUID(as_uuid=True),
        ForeignKey("clusters.id", ondelete="CASCADE"),
        nullable=False,
    )

    volume_score = Column(Float, default=0)
    spread_score = Column(Float, default=0)
    asta_cita_score = Column(Float, default=0)

    total_score = Column(Float, default=0)
    priority_level = Column(String(30), default="low")
    should_generate_brief = Column(Boolean, default=False)

    computed_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    cluster = relationship(
        "Cluster",
        back_populates="scores",
    )
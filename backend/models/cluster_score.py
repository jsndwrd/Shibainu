import uuid
from sqlalchemy import (
    Column,
    Float,
    DateTime,
    ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from core.database import Base

class ClusterScore(Base):
    __tablename__ = "cluster_scores"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cluster_id = Column(
        UUID(as_uuid=True),
        ForeignKey("clusters.id", ondelete="CASCADE"),
        nullable=False
    )
    volume_score = Column(Float, default=0)
    urgency_score = Column(Float, default=0)
    geo_spread_score = Column(Float, default=0)
    impact_score = Column(Float, default=0)
    total_score = Column(Float, default=0)
    equity_adjusted_score = Column(Float, default=0)
    computed_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    cluster = relationship(
        "Cluster",
        back_populates="scores"
    )
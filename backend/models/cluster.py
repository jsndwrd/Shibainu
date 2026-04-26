import uuid

from sqlalchemy import Column, String, Integer, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from core.database import Base


class Cluster(Base):
    __tablename__ = "clusters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    label = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=False)

    member_count = Column(Integer, nullable=False, default=0)
    avg_urgency = Column(Float, nullable=False, default=0)
    top_provinces = Column(ARRAY(String), nullable=False, default=list)

    priority_score = Column(Float, nullable=False, default=0)

    population = Column(Integer, nullable=False, default=0)
    dominant_asta_cita = Column(String(150), nullable=True)
    asta_confidence = Column(Float, nullable=False, default=0)

    sub_topics = Column(ARRAY(String), nullable=False, default=list)
    urgency_dist = Column(JSONB, nullable=False, default=dict)
    centroid = Column(ARRAY(Float), nullable=False, default=list)
    dominant_impact_scope = Column(String(100), nullable=True)
    metadata_json = Column(JSONB, nullable=False, default=dict)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    aspirations = relationship(
        "Aspiration",
        back_populates="cluster",
    )

    scores = relationship(
        "ClusterScore",
        back_populates="cluster",
        cascade="all, delete-orphan",
    )

    briefs = relationship(
        "PolicyBrief",
        back_populates="cluster",
        cascade="all, delete-orphan",
    )
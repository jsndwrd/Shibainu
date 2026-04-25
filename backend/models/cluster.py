import uuid

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.database import Base


class Cluster(Base):
    __tablename__ = "clusters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    label = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)

    centroid = Column(ARRAY(Float), nullable=True)

    member_count = Column(Integer, default=1)
    top_provinces = Column(ARRAY(String), default=[])

    dominant_asta_cita = Column(String(50), nullable=True)
    asta_confidence = Column(Float, default=0.75)

    sub_topics = Column(ARRAY(String), default=[])
    dominant_impact_scope = Column(String(30), nullable=True)

    metadata_json = Column(JSONB, default={})

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

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
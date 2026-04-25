import uuid

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
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
        nullable=False,
        index=True,
    )

    content = Column(Text, nullable=False)
    urgency_classification = Column(String(100), nullable=False)
    generated_by = Column(String(100), nullable=False, default="system")

    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    cluster = relationship(
        "Cluster",
        back_populates="briefs",
    )
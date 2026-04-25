import uuid
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    DateTime,
    ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from pgvector.sqlalchemy import Vector

from core.database import Base


class Aspiration(Base):
    __tablename__ = "aspirations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    citizen_id = Column(
        UUID(as_uuid=True),
        ForeignKey("citizens.id", ondelete="CASCADE"),
        nullable=False
    )

    description = Column(Text, nullable=False)
    cleaned_description = Column(Text, nullable=True)

    category_user_input = Column(String(50), nullable=True)
    predicted_category = Column(String(50), nullable=True)

    urgency_user_input = Column(Integer, nullable=True)
    predicted_urgency = Column(Integer, nullable=True)

    province = Column(String(100), nullable=False)
    regency = Column(String(100), nullable=False)

    impact_scope = Column(String(30), nullable=False)
    target_level = Column(String(30), nullable=False)

    embedding = Column(Vector(768), nullable=True)

    cluster_id = Column(
        UUID(as_uuid=True),
        ForeignKey("clusters.id", ondelete="SET NULL"),
        nullable=True
    )

    status = Column(String(30), default="received")

    submitted_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    citizen = relationship(
        "Citizen",
        back_populates="aspirations"
    )

    cluster = relationship(
        "Cluster",
        back_populates="aspirations"
    )
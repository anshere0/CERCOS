"""Operational audit logs and ETL data quarantine models."""
from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class RecommendationsLog(Base):
    """Audit log of recommendation requests and MCDM calculation results."""

    __tablename__ = "recommendations_log"
    __table_args__ = ({"schema": "cercos"},)

    rec_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, server_default=func.now()
    )
    request: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    response: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    mode: Mapped[str | None] = mapped_column(String(20), nullable=True)
    engine_version: Mapped[str | None] = mapped_column(String(20), nullable=True)


class ETLReject(Base):
    """Quarantine table storing malformed or unvalidated upstream rows with failure reasons."""

    __tablename__ = "etl_rejects"
    __table_args__ = ({"schema": "cercos"},)

    reject_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job: Mapped[str | None] = mapped_column(String(40), nullable=True)
    raw: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, server_default=func.now()
    )

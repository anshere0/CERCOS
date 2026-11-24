"""Field research models: anonymous survey responses and station queue observations."""
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SurveyResponse(Base):
    """Anonymous driver BWM pairwise ranking survey.

    Strict zero PII rule: absolutely no driver names, telephone numbers, or license plates.
    """

    __tablename__ = "survey_responses"
    __table_args__ = (
        CheckConstraint("range_anxiety BETWEEN 1 AND 5", name="ck_survey_range_anxiety"),
        CheckConstraint("consent = TRUE", name="ck_survey_consent"),
        {"schema": "cercos"},
    )

    response_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    segment: Mapped[str] = mapped_column(String(10), nullable=False)
    vehicle_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    area: Mapped[str | None] = mapped_column(String(60), nullable=True)
    home_charging: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    range_anxiety: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    best_criterion: Mapped[str] = mapped_column(String(20), nullable=False)
    worst_criterion: Mapped[str] = mapped_column(String(20), nullable=False)
    best_to_others: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    others_to_worst: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    wtp_zero_wait_inr: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    consent: Mapped[bool] = mapped_column(Boolean, nullable=False)
    enumerator: Mapped[str | None] = mapped_column(String(40), nullable=True)


class StationObservation(Base):
    """Queueing and utilization observations collected at physical charging stations."""

    __tablename__ = "station_observations"
    __table_args__ = (
        CheckConstraint("slot IN ('07-10', '12-15', '18-21')", name="ck_station_obs_slot"),
        {"schema": "cercos"},
    )

    obs_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    station_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("cercos.charging_stations.station_id"), nullable=False
    )
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    slot: Mapped[str | None] = mapped_column(String(10), nullable=True)
    vehicles_waiting: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    connectors_busy: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    arrivals_in_interval: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    interval_minutes: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    session_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    session_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    kwh_delivered: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    observer: Mapped[str | None] = mapped_column(String(40), nullable=True)

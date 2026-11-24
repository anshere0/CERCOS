"""Charging station and connector relational models."""
from datetime import datetime
from decimal import Decimal

from geoalchemy2 import Geometry
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ChargingStation(Base):
    """EV Charging station model with PostGIS Point geometry and multi-source provenance."""

    __tablename__ = "charging_stations"
    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 5", name="ck_charging_stations_rating"),
        CheckConstraint(
            "source IN ('osm', 'ocm', 'census', 'fixture', 'synthetic', 'manual')",
            name="ck_charging_stations_source",
        ),
        CheckConstraint("confidence BETWEEN 0 AND 1", name="ck_charging_stations_confidence"),
        {"schema": "cercos"},
    )

    station_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cpo_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    station_name: Mapped[str] = mapped_column(String(150), nullable=False)
    district_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("cercos.districts.district_id"), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    max_power_kw: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    tariff_inr_kwh: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    rating: Mapped[Decimal | None] = mapped_column(Numeric(2, 1), nullable=True)
    is_operational: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    open_24x7: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    hours_text: Mapped[str | None] = mapped_column(String(100), nullable=True)
    contact: Mapped[str | None] = mapped_column(String(100), nullable=True)
    geom = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=False)

    # Provenance tracking
    source: Mapped[str] = mapped_column(String(30), nullable=False)
    source_ref: Mapped[str | None] = mapped_column(String(200), nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    confidence: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False)

    # Cascade relationship to connectors
    connectors: Mapped[list["Connector"]] = relationship(
        "Connector", back_populates="station", cascade="all, delete-orphan"
    )


class Connector(Base):
    """Physical charging plug/connector attached to a charging station."""

    __tablename__ = "connectors"
    __table_args__ = (
        CheckConstraint(
            "status IN ('AVAILABLE', 'OCCUPIED', 'FAULTY', 'OFFLINE', 'UNKNOWN')",
            name="ck_connectors_status",
        ),
        {"schema": "cercos"},
    )

    connector_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    station_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("cercos.charging_stations.station_id", ondelete="CASCADE"), nullable=False
    )
    connector_type: Mapped[str] = mapped_column(String(30), nullable=False)
    output_power_kw: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="UNKNOWN")

    station: Mapped["ChargingStation"] = relationship("ChargingStation", back_populates="connectors")

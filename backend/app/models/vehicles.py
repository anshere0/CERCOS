"""Vehicle catalog and technical charging limits."""
from decimal import Decimal

from sqlalchemy import CheckConstraint, Column, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Vehicle(Base):
    """EV technical catalog model recording battery capacity, consumption, and connector types."""

    __tablename__ = "vehicles"
    __table_args__ = (
        CheckConstraint("segment IN ('E2W', 'E3W', 'E4W', 'ELCV')", name="ck_vehicles_segment"),
        {"schema": "cercos"},
    )

    vehicle_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    segment: Mapped[str] = mapped_column(String(10), nullable=False)
    battery_kwh: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    wh_per_km: Mapped[Decimal | None] = mapped_column(Numeric(6, 1), nullable=True)
    max_dc_kw: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    max_ac_kw: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    connector_types = Column(ARRAY(String), nullable=True)

    # Provenance
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False)

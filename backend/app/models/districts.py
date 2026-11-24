"""District spatial and transportation model."""
from datetime import datetime
from decimal import Decimal

from geoalchemy2 import Geometry
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class District(Base):
    """Administrative district model storing EV registration numbers and MultiPolygon geometry."""

    __tablename__ = "districts"
    __table_args__ = (
        CheckConstraint("confidence BETWEEN 0 AND 1", name="ck_districts_confidence"),
        {"schema": "cercos"},
    )

    district_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    district_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    rto_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    is_model_ev_city: Mapped[bool] = mapped_column(Boolean, default=False)
    ev_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ev_e2w: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ev_e3w: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ev_e4w: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ev_other: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ev_data_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    geom = mapped_column(Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=True)

    # Provenance tracking
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(3, 2), nullable=True)

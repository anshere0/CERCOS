"""Pydantic v2 schemas for vehicle intake profiles."""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

VehicleSegment = Literal["E2W", "E3W", "E4W", "ELCV"]


class VehicleBase(BaseModel):
    """Base vehicle schema with technical charging envelope."""
    model_name: str
    segment: VehicleSegment
    battery_kwh: float | None = Field(None, gt=0)
    wh_per_km: float | None = Field(None, gt=0)
    max_dc_kw: float | None = Field(None, ge=0)
    max_ac_kw: float | None = Field(None, ge=0)
    connector_types: list[str] = []

    # Provenance
    source: str
    confidence: float = Field(..., ge=0.0, le=1.0)


class VehicleCreate(VehicleBase):
    """Schema for inserting a vehicle into the catalog."""


class VehicleRead(VehicleBase):
    """Schema for reading a vehicle with ID."""
    model_config = ConfigDict(from_attributes=True)
    vehicle_id: int

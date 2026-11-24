"""Pydantic v2 schemas for charging stations and connectors."""
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ConnectorBase(BaseModel):
    """Base connector schema."""
    connector_type: str
    output_power_kw: float = Field(..., gt=0)
    status: Literal["AVAILABLE", "OCCUPIED", "FAULTY", "OFFLINE", "UNKNOWN"] = "UNKNOWN"


class ConnectorCreate(ConnectorBase):
    """Connector creation schema."""


class ConnectorRead(ConnectorBase):
    """Connector read schema."""
    model_config = ConfigDict(from_attributes=True)
    connector_id: int
    station_id: int


StationSource = Literal["osm", "ocm", "census", "fixture", "synthetic", "manual"]


class StationBase(BaseModel):
    """Base station schema including mandatory provenance tracking."""
    station_name: str
    cpo_name: str | None = None
    district_id: int | None = None
    address: str | None = None
    max_power_kw: float | None = None
    tariff_inr_kwh: float | None = None
    rating: float | None = Field(None, ge=1.0, le=5.0)
    is_operational: bool | None = True
    open_24x7: bool | None = True
    hours_text: str | None = None
    contact: str | None = None
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)

    # Provenance fields
    source: StationSource
    source_ref: str | None = None
    confidence: float = Field(..., ge=0.0, le=1.0)


class StationCreate(StationBase):
    """Schema for creating a new charging station."""
    connectors: list[ConnectorCreate] = []


class StationRead(StationBase):
    """Schema for reading a charging station with ID and fetched timestamp."""
    model_config = ConfigDict(from_attributes=True)
    station_id: int
    fetched_at: datetime
    connectors: list[ConnectorRead] = []


StationResponse = StationRead  # Alias for contract compatibility


class GeoJSONGeometry(BaseModel):
    """Point geometry representation for GeoJSON."""
    type: Literal["Point"] = "Point"
    coordinates: list[float]  # [longitude, latitude]


class StationFeature(BaseModel):
    """GeoJSON Feature representation of a charging station."""
    type: Literal["Feature"] = "Feature"
    geometry: GeoJSONGeometry
    properties: dict[str, Any]


class StationFeatureCollection(BaseModel):
    """GeoJSON FeatureCollection containing charging stations."""
    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[StationFeature]

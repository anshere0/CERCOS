"""Pydantic v2 schemas for the /v1/recommend algorithmic interface."""
from typing import Any, Literal

from pydantic import BaseModel, Field

DecisionMode = Literal["Cheapest", "Fastest", "Shortest", "HighestRated", "BatterySafe", "Balanced"]
FleetSegment = Literal["E2W", "E3W", "E4W", "ELCV"]


class LatLon(BaseModel):
    """Geographic coordinate representation."""
    lat: float = Field(..., ge=-90.0, le=90.0)
    lon: float = Field(..., ge=-180.0, le=180.0)


class RecommendRequest(BaseModel):
    """Request payload for route charging recommendations matching contracts/engine_interface.md."""
    origin: LatLon
    destination: LatLon
    soc_pct: float = Field(..., ge=0.0, le=100.0)
    mode: DecisionMode
    segment: FleetSegment
    vehicle_id: int | None = None
    route_km: float | None = None
    route_geojson: dict[str, Any] | None = None


class CriteriaValues(BaseModel):
    """Normalized criteria values used in MCDM calculation."""
    detour_km: float
    cost_inr_kwh: float
    wait_min: float
    effective_kw: float
    rating: float
    arrival_soc_pct: float


class CriterionExplain(BaseModel):
    """Contribution and qualitative explanation for each decision criterion."""
    criterion: str
    contribution: float
    note: str | None = None


class TopStationResult(BaseModel):
    """Top-ranked recommended charging station."""
    station_id: int
    name: str
    cpo_name: str | None = None
    lat: float | None = None
    lon: float | None = None
    connectors: list[str] = []
    score: float
    rank: int
    eta_extra_min: float
    est_cost_inr: float
    est_charge_min: float
    arrival_soc_pct: float
    criteria: CriteriaValues
    explain: list[CriterionExplain] = []
    source: str
    confidence: float


class RejectedStation(BaseModel):
    """Station filtered out during candidate evaluation with rejection reason."""
    station_id: int
    reason: str


class RecommendResult(BaseModel):
    """Recommendation response payload matching contracts/engine_interface.md."""
    needs_charging: bool
    reachable_km: float
    route_km: float | None = None
    top3: list[TopStationResult] = []
    rejected: list[RejectedStation] = []
    nearest_baseline: dict[str, Any] | None = None
    warnings: list[str] = []
    engine_version: str

"""Pydantic v2 schemas package initialization."""
from app.schemas.field import (
    CensusRecord,
    QueueObservationCreate,
    QueueObservationRead,
    SurveyResponseCreate,
    SurveyResponseRead,
)
from app.schemas.recommend import (
    LatLon,
    RecommendRequest,
    RecommendResult,
    TopStationResult,
)
from app.schemas.station import (
    ConnectorCreate,
    ConnectorRead,
    StationCreate,
    StationFeature,
    StationFeatureCollection,
    StationRead,
    StationResponse,
)
from app.schemas.vehicle import VehicleCatalogItem, VehicleCreate, VehicleRead

__all__ = [
    "CensusRecord",
    "ConnectorCreate",
    "ConnectorRead",
    "LatLon",
    "QueueObservationCreate",
    "QueueObservationRead",
    "RecommendRequest",
    "RecommendResult",
    "StationCreate",
    "StationFeature",
    "StationFeatureCollection",
    "StationRead",
    "StationResponse",
    "SurveyResponseCreate",
    "SurveyResponseRead",
    "TopStationResult",
    "VehicleCatalogItem",
    "VehicleCreate",
    "VehicleRead",
]

"""Geospatial charging station queries and detailed station lookups backed by persistent DB."""
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.core.db import fetch_stations_from_db
from app.schemas.station import (
    GeoJSONGeometry,
    StationFeature,
    StationFeatureCollection,
    StationRead,
)

router = APIRouter()


def get_all_stations(source: str | None = None) -> list[dict[str, Any]]:
    """Load all stations from active database layer (PostgreSQL/PostGIS or seeded local SQLite)."""
    stations = fetch_stations_from_db(source=source)
    for st in stations:
        if isinstance(st.get("fetched_at"), str):
            try:
                st["fetched_at"] = datetime.fromisoformat(st["fetched_at"])
            except ValueError:
                st["fetched_at"] = datetime(2026, 11, 24, 0, 0, 0, tzinfo=UTC)
        elif st.get("fetched_at") is None:
            st["fetched_at"] = datetime(2026, 11, 24, 0, 0, 0, tzinfo=UTC)
    return stations


@router.get("/stations", response_model=StationFeatureCollection)
def get_stations_in_bbox(
    bbox: str = Query(
        ...,
        description="Bounding box query in format 'minLon,minLat,maxLon,maxLat' (e.g. 75.5,22.5,77.8,23.5)",
    ),
    source: str | None = Query(None, description="Filter by data source (e.g. osm, ocm, census, fixture)"),
) -> StationFeatureCollection:
    """Bounding box spatial query returning GeoJSON FeatureCollection with provenance attributes."""
    try:
        parts = [float(p.strip()) for p in bbox.split(",")]
        if len(parts) != 4:
            raise ValueError
        min_lon, min_lat, max_lon, max_lat = parts
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Invalid bbox format. Expected 'minLon,minLat,maxLon,maxLat' as 4 comma-separated numbers.",
        )

    all_stations = get_all_stations(source=source)
    features: list[StationFeature] = []

    for s in all_stations:
        lon = float(s["longitude"])
        lat = float(s["latitude"])

        if not (min_lon <= lon <= max_lon and min_lat <= lat <= max_lat):
            continue

        conns = s.get("connectors", [])
        connector_types = sorted({c.get("connector_type", "Type2") for c in conns if isinstance(c, dict)})
        fetched_iso = (
            s["fetched_at"].isoformat() if isinstance(s["fetched_at"], datetime) else str(s["fetched_at"])
        )

        feature = StationFeature(
            type="Feature",
            geometry=GeoJSONGeometry(type="Point", coordinates=[lon, lat]),
            properties={
                "station_id": s["station_id"],
                "name": s["station_name"],
                "station_name": s["station_name"],
                "cpo_name": s.get("cpo_name"),
                "address": s.get("address"),
                "max_power_kw": s.get("max_power_kw"),
                "tariff_inr_kwh": s.get("tariff_inr_kwh"),
                "rating": s.get("rating"),
                "is_operational": s.get("is_operational", True),
                "open_24x7": s.get("open_24x7", True),
                "hours_text": s.get("hours_text"),
                "contact": s.get("contact"),
                "source": s["source"],
                "source_ref": s.get("source_ref"),
                "confidence": s["confidence"],
                "fetched_at": fetched_iso,
                "connector_types": connector_types,
                "connectors": conns,
            },
        )
        features.append(feature)

    return StationFeatureCollection(type="FeatureCollection", features=features)


@router.get("/stations/{id}", response_model=StationRead)
def get_station_detail(id: int) -> dict[str, Any]:
    """Detailed profile lookup for a specific charging station with 404 handler."""
    all_stations = get_all_stations()
    station = next((s for s in all_stations if s["station_id"] == id), None)

    if station is None:
        raise HTTPException(status_code=404, detail=f"Charging station with id {id} not found.")

    return station

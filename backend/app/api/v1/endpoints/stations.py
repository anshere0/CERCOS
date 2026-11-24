"""Geospatial charging station queries and detailed station lookups."""
from datetime import UTC, datetime
from typing import Any

from app.schemas.station import (
    GeoJSONGeometry,
    StationFeature,
    StationFeatureCollection,
    StationRead,
)
from fastapi import APIRouter, HTTPException, Query

from db.seeds.seed_fixtures import load_fixture_stations

router = APIRouter()


def get_all_stations() -> list[dict[str, Any]]:
    """Load all stations from seeds fixture with generated sequential station_ids."""
    raw_fixtures = load_fixture_stations()
    stations: list[dict[str, Any]] = []

    for idx, s in enumerate(raw_fixtures, start=1):
        station = dict(s)
        station["station_id"] = idx
        station["fetched_at"] = datetime(2026, 2, 15, 0, 0, 0, tzinfo=UTC)
        # Ensure connector IDs
        conns: list[dict[str, Any]] = []
        for c_idx, c in enumerate(station.get("connectors", []), start=1):
            conn = dict(c)
            conn["connector_id"] = idx * 100 + c_idx
            conn["station_id"] = idx
            conns.append(conn)
        station["connectors"] = conns
        stations.append(station)

    return stations


@router.get("/stations", response_model=StationFeatureCollection)
def get_stations_in_bbox(
    bbox: str = Query(
        ...,
        description="Bounding box query in format 'minLon,minLat,maxLon,maxLat' (e.g. 75.5,22.5,77.8,23.5)",
    ),
    source: str | None = Query(None, description="Filter by data source (e.g. fixture, osm, ocm, census)"),
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

    all_stations = get_all_stations()
    features: list[StationFeature] = []

    for s in all_stations:
        lon = s["longitude"]
        lat = s["latitude"]

        if not (min_lon <= lon <= max_lon and min_lat <= lat <= max_lat):
            continue

        if source and s.get("source") != source:
            continue

        feature = StationFeature(
            type="Feature",
            geometry=GeoJSONGeometry(type="Point", coordinates=[lon, lat]),
            properties={
                "station_id": s["station_id"],
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
                "fetched_at": s["fetched_at"].isoformat(),
                "connectors": s.get("connectors", []),
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

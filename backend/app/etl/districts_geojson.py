"""Madhya Pradesh administrative district GeoJSON boundary ingestion pipeline.

Parses MultiPolygon boundaries, identifies model EV cities (Bhopal, Indore),
and stores district spatial envelopes with 0.95 provenance confidence.
"""
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

MODEL_EV_CITIES = {"Bhopal", "Indore"}
CORRIDOR_RTO_CODES = {
    "Bhopal": "MP-04",
    "Sehore": "MP-37",
    "Dewas": "MP-41",
    "Indore": "MP-09",
}


def parse_district_feature(
    feature: dict[str, Any],
    fetched_at: datetime | None = None,
) -> dict[str, Any] | None:
    """Parse a single GeoJSON feature representing an administrative district."""
    props = feature.get("properties") or {}
    geom = feature.get("geometry") or {}

    district_name = (
        props.get("district_name")
        or props.get("district")
        or props.get("NAME_2")
        or props.get("name")
    )
    if not district_name:
        return None

    name_clean = str(district_name).strip().title()
    rto = props.get("rto_code") or CORRIDOR_RTO_CODES.get(name_clean)
    is_model = name_clean in MODEL_EV_CITIES or props.get("is_model_ev_city", False)
    timestamp = fetched_at or datetime.now(UTC)

    # Geometry validation
    geom_type = geom.get("type")
    coords = geom.get("coordinates")
    if not geom_type or not coords:
        return None

    # Standardize to MultiPolygon if Polygon
    if geom_type == "Polygon":
        standardized_geom = {
            "type": "MultiPolygon",
            "coordinates": [coords],
        }
    elif geom_type == "MultiPolygon":
        standardized_geom = geom
    else:
        return None

    return {
        "district_name": name_clean,
        "rto_code": rto,
        "is_model_ev_city": bool(is_model),
        "ev_total": None,
        "ev_e2w": None,
        "ev_e3w": None,
        "ev_e4w": None,
        "ev_other": None,
        "ev_data_year": None,
        "geom": standardized_geom,
        "source": "mp_gis_geojson",
        "fetched_at": timestamp,
        "confidence": 0.95,
    }


def parse_districts_geojson(
    geojson_data: dict[str, Any] | str | Path,
    fetched_at: datetime | None = None,
) -> list[dict[str, Any]]:
    """Parse entire GeoJSON FeatureCollection of districts."""
    if isinstance(geojson_data, (str, Path)):
        p = Path(geojson_data)
        if p.exists() and p.is_file():
            content = json.loads(p.read_text(encoding="utf-8"))
        else:
            content = json.loads(str(geojson_data))
    else:
        content = geojson_data

    features = content.get("features") or []
    districts: list[dict[str, Any]] = []
    seen: set[str] = set()

    for feat in features:
        parsed = parse_district_feature(feat, fetched_at=fetched_at)
        if parsed and parsed["district_name"] not in seen:
            seen.add(parsed["district_name"])
            districts.append(parsed)

    return districts

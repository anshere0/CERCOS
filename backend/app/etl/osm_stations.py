"""OpenStreetMap (Overpass API) charging station ingestion and normalization pipeline.

Queries Overpass for amenity=charging_station, parses nodes and way centroids,
normalizes socket tags to CERCOS contract types, and quarantines invalid records into etl_rejects.
"""
import re
from datetime import UTC, datetime
from typing import Any

BHOPAL_LAT = 23.2599
BHOPAL_LON = 77.4126
MP_BBOX = (21.0, 74.0, 26.9, 82.8)  # (min_lat, min_lon, max_lat, max_lon)

# Mapping from OSM socket keys/values to standard CERCOS connector types
SOCKET_TAG_MAPPING = {
    "socket:type2_combo": "CCS2",
    "socket:ccs": "CCS2",
    "socket:ccs2": "CCS2",
    "socket:type2": "Type2",
    "socket:type2_cable": "Type2",
    "socket:chademo": "CHAdeMO",
    "socket:gbt": "GB/T",
    "socket:gb_t": "GB/T",
    "socket:schuko": "15A_Socket",
    "socket:domestic": "15A_Socket",
    "socket:15a": "15A_Socket",
    "socket:bharat_ac001": "Bharat_AC001",
    "socket:bharat_dc001": "Bharat_DC001",
    "socket:leccs": "LECCS",
}

DEFAULT_CONNECTOR_POWER = {
    "CCS2": 50.0,
    "Type2": 7.4,
    "CHAdeMO": 50.0,
    "GB/T": 15.0,
    "15A_Socket": 3.3,
    "Bharat_AC001": 10.0,
    "Bharat_DC001": 15.0,
    "LECCS": 3.3,
    "Other": 3.3,
}


def build_overpass_query(
    bbox: tuple[float, float, float, float] | None = None,
    around_center: tuple[float, float] | None = (BHOPAL_LAT, BHOPAL_LON),
    around_radius_meters: int = 100000,
) -> str:
    """Construct an Overpass QL query string for charging stations."""
    if around_center:
        lat, lon = around_center
        spatial_filter = f"(around:{around_radius_meters},{lat},{lon})"
    elif bbox:
        min_lat, min_lon, max_lat, max_lon = bbox
        spatial_filter = f"({min_lat},{min_lon},{max_lat},{max_lon})"
    else:
        min_lat, min_lon, max_lat, max_lon = MP_BBOX
        spatial_filter = f"({min_lat},{min_lon},{max_lat},{max_lon})"

    query = f"""[out:json][timeout:60];
(
  node["amenity"="charging_station"]{spatial_filter};
  way["amenity"="charging_station"]{spatial_filter};
);
out body center tags;
"""
    return query


def extract_coordinates(element: dict[str, Any]) -> tuple[float | None, float | None]:
    """Extract latitude and longitude from an OSM node or way centroid."""
    lat: float | None = None
    lon: float | None = None

    if element.get("type") == "node":
        lat = element.get("lat")
        lon = element.get("lon")
    elif element.get("type") == "way":
        center = element.get("center", {})
        lat = center.get("lat")
        lon = center.get("lon")
        if lat is None or lon is None:
            bounds = element.get("bounds", {})
            if "minlat" in bounds and "maxlat" in bounds:
                lat = (bounds["minlat"] + bounds["maxlat"]) / 2.0
                lon = (bounds["minlon"] + bounds["maxlon"]) / 2.0

    return lat, lon


def normalize_connectors(tags: dict[str, Any], max_power_hint: float | None = None) -> list[dict[str, Any]]:
    """Inspect OSM tags and return normalized connector dictionaries."""
    connectors: list[dict[str, Any]] = []

    for tag_key, tag_val in tags.items():
        if tag_key.lower() in SOCKET_TAG_MAPPING:
            standard_type = SOCKET_TAG_MAPPING[tag_key.lower()]
            # Try to parse count
            count = 1
            try:
                parsed_count = int(tag_val)
                if parsed_count > 0:
                    count = parsed_count
            except (ValueError, TypeError):
                count = 1

            output_kw = max_power_hint or DEFAULT_CONNECTOR_POWER.get(standard_type, 7.4)
            for _ in range(min(count, 8)):
                connectors.append({
                    "connector_type": standard_type,
                    "output_power_kw": output_kw,
                    "status": "AVAILABLE",
                })

    # If no socket tags found, fallback to capacity or default
    if not connectors:
        capacity_str = tags.get("capacity", "1")
        try:
            capacity = max(1, min(int(capacity_str), 8))
        except (ValueError, TypeError):
            capacity = 1

        fallback_type = "CCS2" if max_power_hint and max_power_hint >= 30.0 else "Type2"
        fallback_kw = max_power_hint or DEFAULT_CONNECTOR_POWER[fallback_type]
        for _ in range(capacity):
            connectors.append({
                "connector_type": fallback_type,
                "output_power_kw": fallback_kw,
                "status": "AVAILABLE",
            })

    return connectors


def parse_osm_element(
    element: dict[str, Any],
    fetched_at: datetime | None = None,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Parse a raw OSM element into a standardized station dict or quarantine rejection.

    Returns:
        (station_data, None) on success
        (None, reject_data) on failure/invalid coordinates
    """
    elem_id = element.get("id")
    elem_type = element.get("type", "node")
    raw_tags = element.get("tags", {})
    timestamp = fetched_at or datetime.now(UTC)

    # 1. Validate coordinates
    lat, lon = extract_coordinates(element)
    if lat is None or lon is None:
        return None, {
            "job": "osm_loader",
            "raw": element,
            "reason": f"Missing geographic coordinates for OSM {elem_type} id={elem_id}",
            "created_at": timestamp,
        }

    try:
        lat_f = float(lat)
        lon_f = float(lon)
    except (ValueError, TypeError):
        return None, {
            "job": "osm_loader",
            "raw": element,
            "reason": f"Malformed coordinates ({lat}, {lon}) for OSM {elem_type} id={elem_id}",
            "created_at": timestamp,
        }

    if not (-90.0 <= lat_f <= 90.0 and -180.0 <= lon_f <= 180.0):
        return None, {
            "job": "osm_loader",
            "raw": element,
            "reason": f"Coordinates out of bounds ({lat_f}, {lon_f}) for OSM {elem_type} id={elem_id}",
            "created_at": timestamp,
        }

    # 2. Extract and normalize station attributes
    operator = raw_tags.get("operator") or raw_tags.get("brand") or raw_tags.get("network")
    name = raw_tags.get("name")
    if not name:
        name = f"{operator} Charging Station" if operator else f"EV Charging Station #{elem_id}"

    # Max power
    max_power: float | None = None
    for power_key in ("socket:max_power", "capacity:kw", "output", "max_power"):
        if power_key in raw_tags:
            match = re.search(r"(\d+(?:\.\d+)?)", str(raw_tags[power_key]))
            if match:
                max_power = float(match.group(1))
                break

    # Hours & 24x7
    opening_hours = raw_tags.get("opening_hours")
    is_24x7 = opening_hours == "24/7" if opening_hours else True

    # Connectors
    connectors = normalize_connectors(raw_tags, max_power_hint=max_power)
    if not max_power and connectors:
        max_power = max(c["output_power_kw"] for c in connectors)

    # Contact & address
    contact = raw_tags.get("contact:phone") or raw_tags.get("phone") or raw_tags.get("contact:email")
    address_parts = [
        raw_tags.get("addr:street"),
        raw_tags.get("addr:city"),
        raw_tags.get("addr:postcode"),
    ]
    address = ", ".join(p for p in address_parts if p) or None

    station_data = {
        "station_name": name,
        "cpo_name": operator,
        "address": address,
        "max_power_kw": max_power,
        "tariff_inr_kwh": None,  # Not reliably provided in OSM
        "rating": None,
        "is_operational": True,
        "open_24x7": is_24x7,
        "hours_text": opening_hours,
        "contact": contact,
        "latitude": lat_f,
        "longitude": lon_f,
        "source": "osm",
        "source_ref": f"osm:{elem_type}/{elem_id}",
        "fetched_at": timestamp,
        "confidence": 0.80,
        "connectors": connectors,
    }

    return station_data, None


def parse_osm_response(
    osm_data: dict[str, Any],
    fetched_at: datetime | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Parse entire Overpass API response JSON into valid stations and reject records."""
    elements = osm_data.get("elements", [])
    valid_stations: list[dict[str, Any]] = []
    rejects: list[dict[str, Any]] = []

    seen_refs: set[str] = set()

    for elem in elements:
        station, reject = parse_osm_element(elem, fetched_at=fetched_at)
        if reject:
            rejects.append(reject)
        elif station:
            ref = station["source_ref"]
            if ref not in seen_refs:
                seen_refs.add(ref)
                valid_stations.append(station)

    return valid_stations, rejects

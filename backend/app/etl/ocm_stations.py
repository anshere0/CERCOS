"""Open Charge Map (OCM) ingestion client and 50m spatial deduplication engine.

Implements Haversine distance spatial clustering to merge duplicate charging station POIs
across OpenStreetMap and Open Charge Map within 50 meters, combining connectors and
escalating confidence to 0.95 for corroborated facilities.
"""
import math
from datetime import UTC, datetime
from typing import Any

EARTH_RADIUS_METERS = 6371000.0  # WGS-84 mean radius
DEDUPE_DISTANCE_THRESHOLD_METERS = 50.0

OCM_CONNECTOR_MAPPING = {
    "ccs (type 2)": "CCS2",
    "ccs": "CCS2",
    "type 2 (socket)": "Type2",
    "type 2 (tethered)": "Type2",
    "type 2": "Type2",
    "chademo": "CHAdeMO",
    "gb/t": "GB/T",
    "gbt": "GB/T",
    "bharat dc-001": "Bharat_DC001",
    "bharat dc001": "Bharat_DC001",
    "bharat ac-001": "Bharat_AC001",
    "bharat ac001": "Bharat_AC001",
    "bs1363": "15A_Socket",
    "wall outlet": "15A_Socket",
    "15a": "15A_Socket",
    "leccs": "LECCS",
}


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points in meters using Haversine formula."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.asin(math.sqrt(min(1.0, max(0.0, a))))

    return EARTH_RADIUS_METERS * c


def normalize_ocm_connector_type(raw_type: str | None) -> str:
    """Normalize OCM ConnectionType title to standard CERCOS enum."""
    if not raw_type:
        return "Type2"
    clean = raw_type.lower().strip()
    for pattern, std in OCM_CONNECTOR_MAPPING.items():
        if pattern in clean:
            return std
    return "Other"


def parse_ocm_poi(
    poi: dict[str, Any],
    fetched_at: datetime | None = None,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Parse an Open Charge Map POI dictionary into standardized station dict or reject record.

    Returns:
        (station_data, None) on success
        (None, reject_data) on missing or malformed coordinates
    """
    poi_id = poi.get("ID")
    address_info = poi.get("AddressInfo") or {}
    operator_info = poi.get("OperatorInfo") or {}
    timestamp = fetched_at or datetime.now(UTC)

    lat = address_info.get("Latitude")
    lon = address_info.get("Longitude")

    if lat is None or lon is None:
        return None, {
            "job": "ocm_loader",
            "raw": poi,
            "reason": f"Missing coordinates in OCM POI ID={poi_id}",
            "created_at": timestamp,
        }

    try:
        lat_f = float(lat)
        lon_f = float(lon)
    except (ValueError, TypeError):
        return None, {
            "job": "ocm_loader",
            "raw": poi,
            "reason": f"Malformed coordinates ({lat}, {lon}) in OCM POI ID={poi_id}",
            "created_at": timestamp,
        }

    if not (-90.0 <= lat_f <= 90.0 and -180.0 <= lon_f <= 180.0):
        return None, {
            "job": "ocm_loader",
            "raw": poi,
            "reason": f"Coordinates out of bounds ({lat_f}, {lon_f}) in OCM POI ID={poi_id}",
            "created_at": timestamp,
        }

    station_name = address_info.get("Title") or f"EV Station OCM-{poi_id}"
    cpo_name = operator_info.get("Title")

    address_lines = [
        address_info.get("AddressLine1"),
        address_info.get("Town"),
        address_info.get("Postcode"),
    ]
    address = ", ".join(line for line in address_lines if line) or None
    contact = address_info.get("ContactTelephone1")

    # Status & Operational
    status_type = poi.get("StatusType") or {}
    is_operational = status_type.get("IsOperational", True)

    # Connections
    raw_conns = poi.get("Connections") or []
    connectors: list[dict[str, Any]] = []
    max_power_kw: float | None = None

    for conn in raw_conns:
        conn_type_obj = conn.get("ConnectionType") or {}
        conn_type_title = conn_type_obj.get("Title")
        normalized_type = normalize_ocm_connector_type(conn_type_title)

        power_kw = conn.get("PowerKW")
        try:
            power_val = float(power_kw) if power_kw is not None else 7.4
        except (ValueError, TypeError):
            power_val = 7.4

        if max_power_kw is None or power_val > max_power_kw:
            max_power_kw = power_val

        qty = conn.get("Quantity") or 1
        try:
            quantity = max(1, min(int(qty), 8))
        except (ValueError, TypeError):
            quantity = 1

        for _ in range(quantity):
            connectors.append({
                "connector_type": normalized_type,
                "output_power_kw": power_val,
                "status": "AVAILABLE" if is_operational else "OUT_OF_SERVICE",
            })

    if not connectors:
        connectors.append({
            "connector_type": "Type2",
            "output_power_kw": 7.4,
            "status": "AVAILABLE",
        })
        max_power_kw = 7.4

    station_data = {
        "station_name": station_name,
        "cpo_name": cpo_name,
        "address": address,
        "max_power_kw": max_power_kw,
        "tariff_inr_kwh": None,
        "rating": None,
        "is_operational": is_operational,
        "open_24x7": True,
        "hours_text": "24/7",
        "contact": contact,
        "latitude": lat_f,
        "longitude": lon_f,
        "source": "ocm",
        "source_ref": f"ocm:{poi_id}",
        "fetched_at": timestamp,
        "confidence": 0.85,
        "connectors": connectors,
    }

    return station_data, None


def merge_two_stations(target: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    """Merge two stations located within 50m of each other.

    Target properties are enriched with candidate data, connectors are combined,
    and confidence is elevated to 0.95 due to multi-source corroboration.
    """
    merged = dict(target)

    # 1. Update name/CPO if target is generic
    if candidate.get("cpo_name") and not merged.get("cpo_name"):
        merged["cpo_name"] = candidate["cpo_name"]
    if not merged.get("address") and candidate.get("address"):
        merged["address"] = candidate["address"]
    if not merged.get("contact") and candidate.get("contact"):
        merged["contact"] = candidate["contact"]

    # 2. Max power is the maximum observed
    p1 = merged.get("max_power_kw") or 0.0
    p2 = candidate.get("max_power_kw") or 0.0
    merged["max_power_kw"] = max(p1, p2) or None

    # 3. Combine connectors without duplicates
    merged_conns = list(merged.get("connectors", []))
    existing_types = {(c["connector_type"], c["output_power_kw"]) for c in merged_conns}

    for conn in candidate.get("connectors", []):
        key = (conn["connector_type"], conn["output_power_kw"])
        if key not in existing_types:
            merged_conns.append(conn)
            existing_types.add(key)

    merged["connectors"] = merged_conns

    # 4. Escalate confidence to 0.95 due to corroboration
    merged["confidence"] = 0.95
    merged["source_ref"] = f"{merged.get('source_ref')}+{candidate.get('source_ref')}"

    return merged


def deduplicate_spatial_stations(
    existing_stations: list[dict[str, Any]],
    incoming_stations: list[dict[str, Any]],
    threshold_meters: float = DEDUPE_DISTANCE_THRESHOLD_METERS,
) -> list[dict[str, Any]]:
    """Deduplicate incoming stations against existing stations within threshold distance.

    Returns the unified, deduplicated list of stations.
    """
    master_stations: list[dict[str, Any]] = [dict(s) for s in existing_stations]

    for incoming in incoming_stations:
        lat2 = incoming["latitude"]
        lon2 = incoming["longitude"]

        matched_idx: int | None = None
        min_dist = float("inf")

        for idx, existing in enumerate(master_stations):
            lat1 = existing["latitude"]
            lon1 = existing["longitude"]
            dist = haversine_distance(lat1, lon1, lat2, lon2)
            if dist <= threshold_meters and dist < min_dist:
                min_dist = dist
                matched_idx = idx

        if matched_idx is not None:
            # Merge with matched station
            master_stations[matched_idx] = merge_two_stations(master_stations[matched_idx], incoming)
        else:
            # Distinct station
            master_stations.append(dict(incoming))

    return master_stations

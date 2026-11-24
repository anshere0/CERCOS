"""Unit and mock fixture tests for the OpenStreetMap Overpass loader.

Verifies query builder, element parsing, tag normalization, and quarantine reject handling.
"""
from datetime import UTC, datetime

from app.etl.osm_stations import (
    build_overpass_query,
    parse_osm_element,
    parse_osm_response,
)


def test_build_overpass_query() -> None:
    """Verify Overpass QL query construction with Bhopal radius and bounding boxes."""
    # Bhopal 100km default query
    q_bhopal = build_overpass_query(around_center=(23.2599, 77.4126), around_radius_meters=100000)
    assert "[out:json]" in q_bhopal
    assert "amenity" in q_bhopal
    assert "charging_station" in q_bhopal
    assert "around:100000,23.2599,77.4126" in q_bhopal

    # Custom bounding box query
    q_bbox = build_overpass_query(bbox=(22.5, 76.5, 23.5, 77.5), around_center=None)
    assert "(22.5,76.5,23.5,77.5)" in q_bbox


def test_parse_valid_osm_node() -> None:
    """Verify parsing a well-formed OSM node with socket and operator tags."""
    node_payload = {
        "type": "node",
        "id": 108849201,
        "lat": 23.2351,
        "lon": 77.4285,
        "tags": {
            "amenity": "charging_station",
            "name": "Tata Power MP Nagar Station",
            "operator": "Tata Power",
            "opening_hours": "24/7",
            "socket:type2_combo": "2",
            "socket:type2": "1",
            "capacity:kw": "60",
            "addr:street": "MP Nagar Zone 1",
            "addr:city": "Bhopal",
            "contact:phone": "+91 755 2550000",
        },
    }

    station, reject = parse_osm_element(node_payload)
    assert reject is None
    assert station is not None

    assert station["station_name"] == "Tata Power MP Nagar Station"
    assert station["cpo_name"] == "Tata Power"
    assert station["latitude"] == 23.2351
    assert station["longitude"] == 77.4285
    assert station["source"] == "osm"
    assert station["source_ref"] == "osm:node/108849201"
    assert station["confidence"] == 0.80
    assert station["open_24x7"] is True
    assert station["max_power_kw"] == 60.0
    assert station["contact"] == "+91 755 2550000"

    # Connectors verification
    types = [c["connector_type"] for c in station["connectors"]]
    assert "CCS2" in types
    assert "Type2" in types
    assert len(station["connectors"]) == 3  # 2x CCS2 + 1x Type2


def test_parse_osm_way_centroid() -> None:
    """Verify way centroids are parsed when node coordinates are represented as center."""
    way_payload = {
        "type": "way",
        "id": 998877,
        "center": {"lat": 23.1812, "lon": 77.3456},
        "tags": {
            "amenity": "charging_station",
            "operator": "Jio-bp pulse",
            "capacity": "2",
        },
    }

    station, reject = parse_osm_element(way_payload)
    assert reject is None
    assert station is not None
    assert station["station_name"] == "Jio-bp pulse Charging Station"
    assert station["latitude"] == 23.1812
    assert station["longitude"] == 77.3456
    assert station["source_ref"] == "osm:way/998877"
    assert len(station["connectors"]) == 2


def test_malformed_coordinate_rejection() -> None:
    """Verify nodes missing coordinates or out of range are quarantined into etl_rejects."""
    # Missing coordinates
    no_coord_node = {
        "type": "node",
        "id": 112233,
        "tags": {"amenity": "charging_station", "name": "Phantom Charger"},
    }
    station, reject = parse_osm_element(no_coord_node)
    assert station is None
    assert reject is not None
    assert reject["job"] == "osm_loader"
    assert "Missing geographic coordinates" in reject["reason"]
    assert reject["raw"]["id"] == 112233

    # Out of bounds coordinates (lat > 90)
    invalid_coord_node = {
        "type": "node",
        "id": 445566,
        "lat": 123.456,
        "lon": 77.412,
        "tags": {"amenity": "charging_station"},
    }
    station2, reject2 = parse_osm_element(invalid_coord_node)
    assert station2 is None
    assert reject2 is not None
    assert "out of bounds" in reject2["reason"]


def test_parse_osm_response_idempotency() -> None:
    """Verify that multiple elements are parsed, rejects separated, and duplicates discarded."""
    payload = {
        "elements": [
            {
                "type": "node",
                "id": 101,
                "lat": 23.25,
                "lon": 77.41,
                "tags": {"amenity": "charging_station", "name": "Station A"},
            },
            {
                "type": "node",
                "id": 101,  # Duplicate ID
                "lat": 23.25,
                "lon": 77.41,
                "tags": {"amenity": "charging_station", "name": "Station A"},
            },
            {
                "type": "node",
                "id": 102,
                # Missing coordinates -> reject
                "tags": {"amenity": "charging_station", "name": "Station B"},
            },
        ]
    }

    stations, rejects = parse_osm_response(payload, fetched_at=datetime.now(UTC))
    assert len(stations) == 1
    assert stations[0]["source_ref"] == "osm:node/101"
    assert len(rejects) == 1
    assert rejects[0]["raw"]["id"] == 102

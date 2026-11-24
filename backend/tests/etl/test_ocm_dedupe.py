"""Unit tests for the Open Charge Map loader and 50m spatial deduplication engine."""
from datetime import UTC, datetime

from app.etl.ocm_stations import (
    deduplicate_spatial_stations,
    haversine_distance,
    parse_ocm_poi,
)


def test_haversine_distance_accuracy() -> None:
    """Verify haversine distance calculation matches known geographic points."""
    # Bhopal DB City Mall (23.2332, 77.4334) to Bhopal MP Nagar Zone 1 (23.2351, 77.4285)
    # Expected approx 540 meters
    dist = haversine_distance(23.2332, 77.4334, 23.2351, 77.4285)
    assert 450.0 < dist < 650.0

    # Same point should have 0 distance
    assert haversine_distance(23.25, 77.41, 23.25, 77.41) == 0.0

    # 50-meter offset test: approx 0.00045 degrees latitude is ~50m
    near_dist = haversine_distance(23.25000, 77.41000, 23.25045, 77.41000)
    assert 40.0 < near_dist < 60.0


def test_parse_valid_ocm_poi() -> None:
    """Verify parsing an OCM POI dictionary with connections and address details."""
    poi = {
        "ID": 298341,
        "AddressInfo": {
            "Title": "Indore Super Corridor Charging Hub",
            "AddressLine1": "Super Corridor Road",
            "Town": "Indore",
            "Postcode": "452005",
            "Latitude": 22.7533,
            "Longitude": 75.8211,
            "ContactTelephone1": "+91 9893000000",
        },
        "OperatorInfo": {"Title": "Fortum Charge & Drive"},
        "StatusType": {"IsOperational": True},
        "Connections": [
            {
                "ConnectionType": {"Title": "CCS (Type 2)"},
                "PowerKW": 60.0,
                "Quantity": 2,
            },
            {
                "ConnectionType": {"Title": "Type 2 (Socket)"},
                "PowerKW": 22.0,
                "Quantity": 1,
            },
        ],
    }

    station, reject = parse_ocm_poi(poi)
    assert reject is None
    assert station is not None

    assert station["station_name"] == "Indore Super Corridor Charging Hub"
    assert station["cpo_name"] == "Fortum Charge & Drive"
    assert station["source"] == "ocm"
    assert station["source_ref"] == "ocm:298341"
    assert station["confidence"] == 0.85
    assert station["max_power_kw"] == 60.0
    assert len(station["connectors"]) == 3  # 2x CCS2 + 1x Type2


def test_parse_ocm_poi_reject_missing_coords() -> None:
    """Verify OCM POI missing coordinates is quarantined to rejects."""
    bad_poi = {
        "ID": 9999,
        "AddressInfo": {"Title": "Missing Coordinates Hub"},
    }
    station, reject = parse_ocm_poi(bad_poi)
    assert station is None
    assert reject is not None
    assert reject["job"] == "ocm_loader"
    assert "Missing coordinates" in reject["reason"]


def test_50m_spatial_deduplication_and_merging() -> None:
    """Verify stations within 50m are merged, connectors combined, and confidence elevated to 0.95."""
    timestamp = datetime.now(UTC)

    # Station A from OSM at (23.25000, 77.41000)
    osm_station = {
        "station_name": "Bhopal Railway EV Point",
        "cpo_name": "Tata Power",
        "address": "Platform 1, Bhopal Junction",
        "max_power_kw": 30.0,
        "latitude": 23.25000,
        "longitude": 77.41000,
        "source": "osm",
        "source_ref": "osm:node/111",
        "confidence": 0.80,
        "fetched_at": timestamp,
        "connectors": [
            {"connector_type": "Type2", "output_power_kw": 22.0, "status": "AVAILABLE"}
        ],
    }

    # Station B from OCM located 20 meters away (~0.00018 deg lat difference)
    ocm_station = {
        "station_name": "Tata Power Bhopal Stn",
        "cpo_name": "Tata Power",
        "address": None,
        "max_power_kw": 60.0,
        "latitude": 23.25018,
        "longitude": 77.41000,
        "source": "ocm",
        "source_ref": "ocm:222",
        "confidence": 0.85,
        "fetched_at": timestamp,
        "connectors": [
            {"connector_type": "CCS2", "output_power_kw": 60.0, "status": "AVAILABLE"}
        ],
    }

    # Station C located 500 meters away (distinct physical facility)
    distant_station = {
        "station_name": "Hamidia Road Fast Charger",
        "cpo_name": "Ather",
        "latitude": 23.25500,
        "longitude": 77.41000,
        "source": "ocm",
        "source_ref": "ocm:333",
        "confidence": 0.85,
        "fetched_at": timestamp,
        "connectors": [
            {"connector_type": "15A_Socket", "output_power_kw": 3.3, "status": "AVAILABLE"}
        ],
    }

    # Run deduplication
    deduped = deduplicate_spatial_stations(
        existing_stations=[osm_station],
        incoming_stations=[ocm_station, distant_station],
        threshold_meters=50.0,
    )

    # We should have exactly 2 stations (osm_station merged with ocm_station, plus distant_station)
    assert len(deduped) == 2

    # Verify the merged station
    merged = deduped[0]
    assert merged["confidence"] == 0.95  # Elevated confidence
    assert merged["max_power_kw"] == 60.0  # Max power updated
    assert "osm:node/111+ocm:222" in merged["source_ref"]

    connector_types = {c["connector_type"] for c in merged["connectors"]}
    assert "Type2" in connector_types
    assert "CCS2" in connector_types

    # Verify distinct station remains untouched
    assert deduped[1]["source_ref"] == "ocm:333"
    assert deduped[1]["confidence"] == 0.85

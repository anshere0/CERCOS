"""Unit tests for the data quality audit engine and corridor seed fixtures."""

from app.etl.data_quality import audit_stations, generate_markdown_audit_report

from db.seeds.seed_fixtures import load_fixture_stations, seed_database


def test_fixture_stations_file_validity() -> None:
    """Ensure db/seeds/fixture_stations.json has 20 corridor stations matching StationCreate schema."""
    stations = load_fixture_stations()
    assert len(stations) == 20, f"Expected 20 stations, found {len(stations)}"

    for s in stations:
        assert s["source"] == "fixture"
        assert s["confidence"] == 0.90
        assert s["latitude"] > 0
        assert s["longitude"] > 0
        assert len(s["connectors"]) >= 1

        # Check corridor bounds (Bhopal to Indore: 22.5 to 23.5 N, 75.5 to 77.8 E)
        assert 22.5 <= s["latitude"] <= 23.5
        assert 75.5 <= s["longitude"] <= 77.8


def test_audit_stations_metrics() -> None:
    """Verify data quality audit computations for completeness, bounds, and duplicates."""
    stations = [
        {
            "station_name": "Hub A",
            "cpo_name": "Tata Power",
            "address": "Bhopal Main",
            "max_power_kw": 50.0,
            "tariff_inr_kwh": 18.0,
            "rating": 4.5,
            "latitude": 23.25,
            "longitude": 77.41,
            "source": "fixture",
            "confidence": 0.90,
            "connectors": [{"connector_type": "CCS2", "output_power_kw": 50.0}],
        },
        {
            "station_name": "Hub B",
            "cpo_name": None,  # Missing CPO
            "address": None,   # Missing address
            "max_power_kw": None,  # Missing power
            "tariff_inr_kwh": None,
            "rating": None,
            "latitude": 23.2501,  # ~11 meters from Hub A -> Duplicate cluster!
            "longitude": 77.4101,
            "source": "osm",
            "confidence": 0.80,
            "connectors": [],
        },
        {
            "station_name": "Hub C (Out of bounds)",
            "cpo_name": "Statiq",
            "address": "Delhi Road",
            "max_power_kw": 60.0,
            "tariff_inr_kwh": 20.0,
            "rating": 4.0,
            "latitude": 28.61,  # Out of corridor bbox
            "longitude": 77.20,
            "source": "ocm",
            "confidence": 0.85,
            "connectors": [{"connector_type": "CCS2", "output_power_kw": 60.0}],
        },
    ]

    stats = audit_stations(stations)
    assert stats["total_stations"] == 3
    assert stats["in_study_corridor"] == 2
    assert stats["out_of_bbox"] == 1
    assert stats["missing_cpo"] == 1
    assert stats["missing_address"] == 1
    assert stats["missing_power"] == 1
    assert stats["duplicate_pairs_under_50m"] == 1

    # Verify markdown generation
    report = generate_markdown_audit_report(stats)
    assert "# CERCOS Data Quality & Audit Report" in report
    assert "**Total Ingested Stations:** 3" in report


def test_seed_database_idempotent() -> None:
    """Verify seed_database returns 20 without database connection."""
    count = seed_database()
    assert count == 20

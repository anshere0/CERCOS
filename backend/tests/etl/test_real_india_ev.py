"""Unit tests for the Madhya Pradesh real EV station ETL pipeline (`fetch_real_india_ev`)."""

from app.etl.fetch_real_india_ev import (
    normalize_upstream_connectors,
    parse_pricing_inr,
    transform_registry_record,
)


def test_parse_pricing_inr_handles_real_formats() -> None:
    """Verify upstream tariff formats including Free, fixed, ranges, and non-numeric labels."""
    assert parse_pricing_inr("₹22/kWh") == 22.0
    assert parse_pricing_inr("₹22.99/kWh") == 22.99
    assert parse_pricing_inr("₹18-24/kWh") == 21.0
    assert parse_pricing_inr("Free") == 0.0
    assert parse_pricing_inr("Paid") is None
    assert parse_pricing_inr(None) is None


def test_ather_grid_normalizes_to_leccs() -> None:
    """Verify Ather Grid stations map cleanly to 3.3 kW LECCS hardware."""
    raw = {
        "name": "GOKULDAS HOSPITAL",
        "operator": "Ather",
        "network": "Ather Grid",
        "address": "DR SARJU PRASAD MARG, Indore",
        "city": "Indore",
        "district": "Indore",
        "state": "Madhya Pradesh",
        "lat": 22.7157725,
        "lng": 75.8759735,
        "connectors": [],
        "sources": ["OpenStreetMap", "Ather Grid"],
        "n_sources": 2,
    }
    st = transform_registry_record(raw, idx=1, fetched_at="2026-11-24T00:00:00Z")
    assert st["source"] == "ocm"
    assert st["confidence"] == 0.90
    assert st["tariff_inr_kwh"] is None
    assert len(st["connectors"]) == 1
    assert st["connectors"][0]["connector_type"] == "LECCS"
    assert st["connectors"][0]["output_power_kw"] == 3.3


def test_bolt_earth_and_chargezone_connectors() -> None:
    """Verify 3-pin/15A and ChargeZone CCS2 preserve gun counts and power."""
    raw_cz = {
        "name": "MP | Ashta | ode da dhaba",
        "operator": "ChargeZone",
        "network": "Gentari",
        "lat": 23.0179251,
        "lng": 76.66818812,
        "connectors": [{"type": "CCS2", "power_kw": 90.0, "count": None}],
        "dc_points": 4,
        "max_power_kw": 60.0,
        "pricing": "₹22/kWh",
        "sources": ["MG eHUB", "ChargeZone", "Kia/Numocity"],
        "n_sources": 3,
    }
    st_cz = transform_registry_record(raw_cz, idx=2, fetched_at="2026-11-24T00:00:00Z")
    assert st_cz["tariff_inr_kwh"] == 22.0
    assert st_cz["confidence"] == 0.95
    assert len(st_cz["connectors"]) == 4
    assert all(c["connector_type"] == "CCS2" for c in st_cz["connectors"])

    conns_b, pw_b, _ = normalize_upstream_connectors(
        {"operator": "Bolt.Earth", "connectors": [{"type": "3-pin/15A", "power_kw": 3.3, "count": 1}]}
    )
    assert pw_b == 3.3
    assert conns_b[0]["connector_type"] == "15A_Socket"

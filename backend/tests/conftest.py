"""Shared test fixtures for CERCOS engine and queue test suites."""
import sys
from pathlib import Path
from typing import Any

# Ensure repository root and backend directory are in sys.path
_repo_root = Path(__file__).resolve().parents[2]
_backend_dir = _repo_root / "backend"
for _path_str in [str(_repo_root), str(_backend_dir)]:
    if _path_str not in sys.path:
        sys.path.insert(0, _path_str)

import pytest
from app.schemas.recommend import LatLon, RecommendRequest


@pytest.fixture
def sample_vehicles() -> dict[str, dict[str, Any]]:
    """Fixture providing vehicle envelopes across all four MP segments."""
    return {
        "E2W": {
            "model_name": "Generic E2W Scooter",
            "segment": "E2W",
            "battery_kwh": 3.7,
            "wh_per_km": 35.0,
            "max_dc_kw": None,
            "max_ac_kw": 1.5,
            "connector_types": ["15A_Socket", "LECCS", "Type2"],
            "source": "datasheet",
            "confidence": 0.95,
        },
        "E3W": {
            "model_name": "Generic E3W Rickshaw",
            "segment": "E3W",
            "battery_kwh": 8.0,
            "wh_per_km": 75.0,
            "max_dc_kw": None,
            "max_ac_kw": 3.3,
            "connector_types": ["15A_Socket", "LECCS", "Type2"],
            "source": "datasheet",
            "confidence": 0.95,
        },
        "E4W": {
            "model_name": "Generic E4W Hatchback",
            "segment": "E4W",
            "battery_kwh": 40.0,
            "wh_per_km": 145.0,
            "max_dc_kw": 50.0,
            "max_ac_kw": 7.2,
            "connector_types": ["CCS2", "Type2"],
            "source": "datasheet",
            "confidence": 0.95,
        },
        "ELCV": {
            "model_name": "Generic e-LCV Cargo",
            "segment": "ELCV",
            "battery_kwh": 25.0,
            "wh_per_km": 180.0,
            "max_dc_kw": 30.0,
            "max_ac_kw": 7.2,
            "connector_types": ["CCS2", "Type2"],
            "source": "datasheet",
            "confidence": 0.95,
        },
    }


@pytest.fixture
def sample_stations() -> list[dict[str, Any]]:
    """Fixture providing realistic candidate stations along Bhopal-Sehore corridor."""
    return [
        {
            "station_id": 1,
            "name": "Tata Power Fast Charger Sehore Bypass",
            "cpo_name": "Tata Power",
            "lat": 23.205,
            "lon": 77.085,
            "max_power_kw": 60.0,
            "tariff_inr_kwh": 19.5,
            "rating": 4.5,
            "is_operational": True,
            "connector_types": ["CCS2", "Type2"],
            "detour_km": 0.8,
            "km_along_route": 35.0,
            "predicted_wait_min": 6.0,
            "source": "osm",
            "confidence": 0.95,
        },
        {
            "station_id": 2,
            "name": "Jio-BP Pulse Charging Hub",
            "cpo_name": "Jio-BP",
            "lat": 23.190,
            "lon": 77.050,
            "max_power_kw": 30.0,
            "tariff_inr_kwh": 16.0,
            "rating": 4.2,
            "is_operational": True,
            "connector_types": ["CCS2", "Type2", "15A_Socket"],
            "detour_km": 1.5,
            "km_along_route": 42.0,
            "predicted_wait_min": 4.0,
            "source": "ocm",
            "confidence": 0.90,
        },
        {
            "station_id": 3,
            "name": "Bhopal Smart City Community Hub",
            "cpo_name": "Bhopal Smart City",
            "lat": 23.245,
            "lon": 77.395,
            "max_power_kw": 15.0,
            "tariff_inr_kwh": 13.5,
            "rating": 3.8,
            "is_operational": True,
            "connector_types": ["Type2", "15A_Socket", "LECCS"],
            "detour_km": 0.3,
            "km_along_route": 12.0,
            "predicted_wait_min": 15.0,
            "source": "osm",
            "confidence": 0.90,
        },
        {
            "station_id": 4,
            "name": "Defective Station Out of Service",
            "cpo_name": "Independent",
            "lat": 23.210,
            "lon": 77.100,
            "max_power_kw": 50.0,
            "tariff_inr_kwh": 15.0,
            "rating": 2.1,
            "is_operational": False,  # Should be rejected
            "connector_types": ["CCS2"],
            "detour_km": 0.5,
            "km_along_route": 30.0,
            "predicted_wait_min": 0.0,
            "source": "osm",
            "confidence": 0.70,
        },
        {
            "station_id": 5,
            "name": "Ultra Far Corridor Station",
            "cpo_name": "Highway CPO",
            "lat": 23.050,
            "lon": 76.800,
            "max_power_kw": 50.0,
            "tariff_inr_kwh": 18.0,
            "rating": 4.0,
            "is_operational": True,
            "connector_types": ["CCS2"],
            "detour_km": 4.0,
            "km_along_route": 150.0,  # Unreachable with low SoC
            "predicted_wait_min": 5.0,
            "source": "osm",
            "confidence": 0.85,
        },
    ]


@pytest.fixture
def sample_recommend_request() -> RecommendRequest:
    """Fixture providing a standard route recommendation request."""
    return RecommendRequest(
        origin=LatLon(lat=23.2599, lon=77.4126),  # Bhopal
        destination=LatLon(lat=23.0150, lon=76.8500),  # Ashta
        soc_pct=35.0,
        mode="Balanced",
        segment="E4W",
        route_km=85.0,
    )

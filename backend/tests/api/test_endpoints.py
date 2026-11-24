"""Comprehensive API contract tests for CERCOS REST endpoints."""
import time
from unittest.mock import patch

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_get_modes_endpoint() -> None:
    """Verify GET /v1/modes returns 6 decision modes and criteria list."""
    response = client.get("/v1/modes")
    assert response.status_code == 200
    data = response.json()
    assert "criteria" in data
    assert "modes" in data
    assert len(data["modes"]) == 6
    assert "Cheapest" in data["modes"]
    assert "Fastest" in data["modes"]
    assert "Balanced" in data["modes"]


def test_get_vehicles_endpoint() -> None:
    """Verify GET /v1/vehicles returns vehicle catalog and filters by segment."""
    response = client.get("/v1/vehicles")
    assert response.status_code == 200
    all_veh = response.json()
    assert len(all_veh) >= 5

    # Filter by segment E4W
    e4w_resp = client.get("/v1/vehicles?segment=E4W")
    assert e4w_resp.status_code == 200
    e4w_veh = e4w_resp.json()
    assert len(e4w_veh) >= 1
    assert all(v["segment"] == "E4W" for v in e4w_veh)


def test_get_stations_bbox_geojson() -> None:
    """Verify GET /v1/stations with bounding box returns valid GeoJSON FeatureCollection."""
    response = client.get("/v1/stations?bbox=75.5,22.5,77.8,23.5")
    assert response.status_code == 200
    fc = response.json()
    assert fc["type"] == "FeatureCollection"
    assert "features" in fc
    assert len(fc["features"]) > 0

    first_feat = fc["features"][0]
    assert first_feat["type"] == "Feature"
    assert first_feat["geometry"]["type"] == "Point"
    props = first_feat["properties"]
    assert "station_id" in props
    assert "station_name" in props
    assert "source" in props
    assert "confidence" in props
    assert "connectors" in props


def test_get_stations_empty_bbox() -> None:
    """Verify bounding box with no stations returns empty FeatureCollection."""
    response = client.get("/v1/stations?bbox=0.0,0.0,1.0,1.0")
    assert response.status_code == 200
    fc = response.json()
    assert fc["type"] == "FeatureCollection"
    assert len(fc["features"]) == 0


def test_get_stations_invalid_bbox_error() -> None:
    """Verify GET /v1/stations rejects malformed bbox with 422."""
    response = client.get("/v1/stations?bbox=invalid,bbox")
    assert response.status_code == 422


def test_get_station_detail_and_404() -> None:
    """Verify GET /v1/stations/{id} returns station detail or 404 if not found."""
    # Valid station
    resp_ok = client.get("/v1/stations/1")
    assert resp_ok.status_code == 200
    station = resp_ok.json()
    assert station["station_id"] == 1
    assert "station_name" in station

    # Not found station
    resp_404 = client.get("/v1/stations/9999")
    assert resp_404.status_code == 404
    assert "not found" in resp_404.json()["detail"].lower()


def test_field_census_submission() -> None:
    """Verify POST /v1/field/census ingests hardware audit with 201 Created."""
    payload = {
        "station_name": "Ashta Toll Fast Charger",
        "cpo_name": "Tata Power",
        "latitude": 23.0185,
        "longitude": 76.5342,
        "max_power_kw": 60.0,
        "tariff_inr_kwh": 18.5,
        "is_operational": True,
        "open_24x7": True,
        "connector_types": ["CCS2", "Type2"],
    }
    response = client.post("/v1/field/census", json=payload)
    assert response.status_code == 201
    assert response.json()["status"] == "created"
    assert response.json()["confidence"] == 0.90


def test_field_survey_consent_gate() -> None:
    """Verify POST /v1/field/survey strictly gates on consent=True and rejects consent=False or PII."""
    valid_survey = {
        "segment": "E4W",
        "vehicle_model": "Tata Nexon EV",
        "area": "Bhopal MP Nagar",
        "home_charging": True,
        "range_anxiety": 4,
        "best_criterion": "cost",
        "worst_criterion": "wait",
        "best_to_others": {"cost": 1, "wait": 5},
        "others_to_worst": {"wait": 1, "cost": 5},
        "consent": True,
    }
    # Success with consent=True
    resp = client.post("/v1/field/survey", json=valid_survey)
    assert resp.status_code == 201
    assert resp.json()["status"] == "created"

    # Rejection with consent=False
    bad_survey = valid_survey.copy()
    bad_survey["consent"] = False
    resp_bad = client.post("/v1/field/survey", json=bad_survey)
    assert resp_bad.status_code == 422

    # Rejection of personal PII (e.g. driver_phone)
    pii_survey = valid_survey.copy()
    pii_survey["driver_phone"] = "9876543210"
    resp_pii = client.post("/v1/field/survey", json=pii_survey)
    assert resp_pii.status_code == 422


def test_field_queue_observation() -> None:
    """Verify POST /v1/field/queue records 3-hour observation slots with 201 Created."""
    payload = {
        "station_id": 1,
        "observed_at": "2026-02-20T14:00:00Z",
        "slot": "12-15",
        "vehicles_waiting": 3,
        "connectors_busy": 2,
        "arrivals_in_interval": 5,
        "interval_minutes": 60,
    }
    response = client.post("/v1/field/queue", json=payload)
    assert response.status_code == 201
    assert response.json()["status"] == "created"
    assert response.json()["station_id"] == 1


def test_field_csv_exports() -> None:
    """Verify GET /v1/field/export/{kind} streams live CSV files for census, survey, and queue."""
    for kind in ("census", "survey", "queue"):
        response = client.get(f"/v1/field/export/{kind}")
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
        assert len(response.text) > 0


def test_field_export_invalid_kind() -> None:
    """Verify GET /v1/field/export/{kind} rejects unsupported kind with 422."""
    response = client.get("/v1/field/export/unsupported")
    assert response.status_code == 422


def test_recommend_endpoint_contract_and_bottleneck() -> None:
    """Verify POST /v1/recommend returns top 3 ranked stations and enforces physical power bottleneck."""
    payload = {
        "origin": {"lat": 23.2599, "lon": 77.4126},      # Bhopal
        "destination": {"lat": 22.7196, "lon": 75.8577}, # Indore
        "soc_pct": 65.0,
        "mode": "Fastest",
        "segment": "E4W",
    }
    response = client.post("/v1/recommend", json=payload)
    assert response.status_code == 200
    res = response.json()

    assert "needs_charging" in res
    assert "reachable_km" in res
    assert "top3" in res
    assert len(res["top3"]) <= 3
    assert len(res["top3"]) > 0

    top_station = res["top3"][0]
    assert "station_id" in top_station
    assert "score" in top_station
    assert "criteria" in top_station
    assert "effective_kw" in top_station["criteria"]

    # Effective power bottleneck: P_eff <= min(station, vehicle max kW)
    assert top_station["criteria"]["effective_kw"] <= 50.0

    assert "engine_version" in res
    assert "warnings" in res
    assert "rejected" in res


def test_recommend_all_modes() -> None:
    """Verify recommendation engine works consistently across all 6 decision modes."""
    modes = ["Cheapest", "Fastest", "Shortest", "HighestRated", "BatterySafe", "Balanced"]
    for mode in modes:
        payload = {
            "origin": {"lat": 23.2599, "lon": 77.4126},
            "destination": {"lat": 22.7196, "lon": 75.8577},
            "soc_pct": 80.0,
            "mode": mode,
            "segment": "E4W",
        }
        resp = client.post("/v1/recommend", json=payload)
        assert resp.status_code == 200
        res = resp.json()
        assert len(res["top3"]) > 0


def test_recommend_low_battery_needs_charging() -> None:
    """Verify needs_charging=True when battery state is low (15%)."""
    payload = {
        "origin": {"lat": 23.2599, "lon": 77.4126},
        "destination": {"lat": 22.7196, "lon": 75.8577},
        "soc_pct": 15.0,
        "mode": "BatterySafe",
        "segment": "E4W",
    }
    resp = client.post("/v1/recommend", json=payload)
    assert resp.status_code == 200
    res = resp.json()
    assert res["needs_charging"] is True


def test_recommend_performance_budget_200_stations() -> None:
    """Verify performance budget: p95 response time < 500 ms for 200 candidate stations."""
    # Synthesize 200 candidate stations along corridor
    mock_200_stations = []
    for i in range(200):
        mock_200_stations.append({
            "station_name": f"Corridor Station {i}",
            "cpo_name": "Tata Power",
            "address": f"NH 46 Km {i}",
            "latitude": 23.25 - (i * 0.0025),
            "longitude": 77.41 - (i * 0.0075),
            "max_power_kw": 60.0,
            "tariff_inr_kwh": 18.0 + (i % 5),
            "rating": 4.0 + (i % 10) * 0.1,
            "is_operational": True,
            "source": "fixture",
            "confidence": 0.90,
            "connectors": [{"connector_type": "CCS2", "output_power_kw": 60.0}],
        })

    payload = {
        "origin": {"lat": 23.2599, "lon": 77.4126},
        "destination": {"lat": 22.7196, "lon": 75.8577},
        "soc_pct": 75.0,
        "mode": "Fastest",
        "segment": "E4W",
    }

    latencies_ms: list[float] = []
    with patch("app.api.v1.endpoints.recommend.load_fixture_stations", return_value=mock_200_stations):
        for _ in range(10):
            t0 = time.perf_counter()
            resp = client.post("/v1/recommend", json=payload)
            t1 = time.perf_counter()
            assert resp.status_code == 200
            latencies_ms.append((t1 - t0) * 1000.0)

    latencies_ms.sort()
    # 95th percentile
    p95 = latencies_ms[int(len(latencies_ms) * 0.95)]
    assert p95 < 500.0, f"p95 latency {p95}ms exceeded 500ms budget"

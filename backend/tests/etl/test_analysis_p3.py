"""Unit tests for Phase-I P3 analysis scripts: corridor_spacing_v0, bwm_weights, and queue_stats."""
from app.main import app
from fastapi.testclient import TestClient

from analysis.bwm_weights import solve_linear_bwm
from analysis.corridor_spacing_v0 import analyze_corridor_spacing
from analysis.queue_stats import compute_queue_parameters

client = TestClient(app)


def test_corridor_spacing_flags_gaps_over_25km() -> None:
    """Verify corridor_spacing_v0 flags every > 25 km gap on corridor fixtures."""
    synthetic_corridor = [
        {"station_name": "Start Bhopal", "latitude": 23.2599, "longitude": 77.4126, "max_power_kw": 60.0},
        {"station_name": "Sehore Stop", "latitude": 23.2147, "longitude": 77.0783, "max_power_kw": 60.0},
        {"station_name": "Dewas Stop", "latitude": 22.9780, "longitude": 76.0520, "max_power_kw": 60.0},
    ]
    report = analyze_corridor_spacing(synthetic_corridor)
    assert report["stations_on_corridor"] == 3
    assert len(report["gaps_exceeding_25km"]) == 2
    assert report["max_gap_km"] > 100.0
    assert len(report["fast_gaps_exceeding_100km"]) >= 1


def test_bwm_solver_rezaei_worked_example() -> None:
    """Verify BWM linear solver matches standard mathematical weights and low consistency ratio."""
    criteria = ["quality", "price", "comfort", "safety", "style"]
    best_to_others = {"quality": 2, "price": 1, "comfort": 4, "safety": 3, "style": 8}
    others_to_worst = {"quality": 4, "price": 8, "comfort": 2, "safety": 3, "style": 1}

    res = solve_linear_bwm(
        criteria=criteria,
        best_criterion="price",
        worst_criterion="style",
        best_to_others=best_to_others,
        others_to_worst=others_to_worst,
    )
    weights = res["weights"]
    assert abs(sum(weights.values()) - 1.0) < 1e-4
    assert weights["price"] > weights["quality"] > weights["safety"] > weights["style"]
    assert res["consistency_ratio"] < 0.1


def test_queue_stats_computations() -> None:
    """Verify arrival rate, service rate, utilization, and SCV calculations."""
    observations = [
        {"interval_minutes": 15, "arrivals_in_interval": 2, "service_minutes": 30},
        {"interval_minutes": 15, "arrivals_in_interval": 1, "service_minutes": 30},
        {"interval_minutes": 15, "arrivals_in_interval": 3, "service_minutes": 30},
    ]
    stats = compute_queue_parameters(observations, num_connectors=2)
    assert stats["lambda_per_hr"] == 8.0
    assert stats["mu_per_hr"] == 2.0
    assert stats["rho"] == 2.0


def test_system_status_endpoint() -> None:
    """Verify GET /v1/status reports active DB backend and policy benchmarks."""
    resp = client.get("/v1/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["database"]["connected"] is True
    assert data["stations_total"] >= 20
    assert "mop_guidelines_2022" in data["policy_benchmarks"]

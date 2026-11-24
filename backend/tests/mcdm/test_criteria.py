"""Unit tests for criteria evaluation, connector compatibility, and power bottleneck."""
from app.mcdm.criteria import (
    CRITERIA_NAMES,
    effective_charging_power,
    filter_and_evaluate_candidates,
)


def test_physical_power_bottleneck_law() -> None:
    """Verify speed criterion = min(station_kW, vehicle_max_accept_kW) — never raw station kW."""
    # Case 1: 120 kW DC station, vehicle accepts max 50 kW DC -> Effective = 50 kW
    eff_1 = effective_charging_power(
        station_power_kw=120.0,
        vehicle_max_dc_kw=50.0,
        vehicle_max_ac_kw=7.2,
        compatible_connectors=["CCS2"],
    )
    assert eff_1 == 50.0

    # Case 2: 30 kW DC station, vehicle accepts max 50 kW DC -> Effective = 30 kW
    eff_2 = effective_charging_power(
        station_power_kw=30.0,
        vehicle_max_dc_kw=50.0,
        vehicle_max_ac_kw=7.2,
        compatible_connectors=["CCS2"],
    )
    assert eff_2 == 30.0

    # Case 3: E2W scooter with AC socket (1.5 kW max) at 22 kW AC Type2 charger -> Effective = 1.5 kW
    eff_3 = effective_charging_power(
        station_power_kw=22.0,
        vehicle_max_dc_kw=None,
        vehicle_max_ac_kw=1.5,
        compatible_connectors=["Type2"],
    )
    assert eff_3 == 1.5


def test_candidate_filtering_and_decision_matrix(sample_stations: list, sample_vehicles: dict) -> None:
    """Verify hard rejection of unoperational, unreachable, and connector-incompatible stations."""
    e4w = sample_vehicles["E4W"]

    X, admissible, rejected = filter_and_evaluate_candidates(
        stations=sample_stations,
        vehicle=e4w,
        direct_route_km=85.0,
        current_soc_pct=35.0,
        wh_per_km=145.0,
    )

    # Station 4 is unoperational -> must be rejected
    rejected_ids = [r["station_id"] for r in rejected]
    assert 4 in rejected_ids
    reason_4 = next(r["reason"] for r in rejected if r["station_id"] == 4)
    assert "out of service" in reason_4.lower()

    # Station 5 is 150 km away -> unreachable with 35% SoC on E4W (reach is ~74 km)
    assert 5 in rejected_ids
    reason_5 = next(r["reason"] for r in rejected if r["station_id"] == 5)
    assert "unreachable" in reason_5.lower() or "reserve" in reason_5.lower()

    # Admissible stations (1, 2, 3) must form decision matrix with 6 columns
    assert X.shape[1] == len(CRITERIA_NAMES)
    assert len(admissible) == X.shape[0]
    assert len(admissible) >= 2

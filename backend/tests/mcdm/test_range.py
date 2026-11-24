"""Unit tests for EV battery range, 8% safety reserve, and consumption models."""
import pytest
from app.mcdm.range import (
    arrival_soc_pct,
    charge_requirements,
    effective_wh_per_km,
    reachable_distance_km,
    usable_energy_kwh,
)


def test_usable_energy_enforces_eight_percent_reserve() -> None:
    """Verify that usable energy strictly deducts the mandatory 8% safety reserve."""
    # 40 kWh battery at 50% SoC has 42% usable SoC above 8% reserve -> 0.42 * 40 = 16.8 kWh
    kwh = usable_energy_kwh(battery_kwh=40.0, current_soc_pct=50.0, reserve_soc_pct=8.0)
    assert pytest.approx(kwh, rel=1e-5) == 16.8

    # When SoC <= 8%, usable energy must be 0.0 kWh (cannot drive into reserve)
    assert usable_energy_kwh(battery_kwh=40.0, current_soc_pct=8.0, reserve_soc_pct=8.0) == 0.0
    assert usable_energy_kwh(battery_kwh=40.0, current_soc_pct=5.0, reserve_soc_pct=8.0) == 0.0


def test_reachable_distance_across_segments(sample_vehicles: dict) -> None:
    """Verify reachable distance calculations across E2W, E3W, E4W, ELCV."""
    # E2W: 3.7 kWh, 35 Wh/km, 100% SoC -> (0.92 * 3.7 * 1000) / 35 approx 97.2 km
    e2w = sample_vehicles["E2W"]
    reach_e2w = reachable_distance_km(
        battery_kwh=e2w["battery_kwh"],
        current_soc_pct=100.0,
        wh_per_km=e2w["wh_per_km"],
    )
    assert 90.0 <= reach_e2w <= 100.0

    # E4W: 40 kWh, 145 Wh/km, 50% SoC -> (0.42 * 40 * 1000) / 145 = 16800 / 145 approx 115.9 km
    e4w = sample_vehicles["E4W"]
    reach_e4w = reachable_distance_km(
        battery_kwh=e4w["battery_kwh"],
        current_soc_pct=50.0,
        wh_per_km=e4w["wh_per_km"],
    )
    assert 110.0 <= reach_e4w <= 120.0


def test_effective_wh_per_km_operating_factors() -> None:
    """Verify consumption multipliers for speed, payload, AC, and gradient."""
    base_wh = 145.0

    # Nominal conditions (45 km/h, 1.0 load, 1.0 AC, 0% grade)
    nominal = effective_wh_per_km(base_wh, speed_kmh=45.0, load_factor=1.0, ac_factor=1.0, gradient_pct=0.0)
    assert pytest.approx(nominal, rel=1e-5) == base_wh

    # High speed penalty (80 km/h)
    high_speed = effective_wh_per_km(base_wh, speed_kmh=80.0)
    assert high_speed > nominal

    # AC active (1.10)
    with_ac = effective_wh_per_km(base_wh, speed_kmh=45.0, ac_factor=1.10)
    assert pytest.approx(with_ac, rel=1e-5) == base_wh * 1.10

    # Uphill gradient (+2%)
    uphill = effective_wh_per_km(base_wh, speed_kmh=45.0, gradient_pct=2.0)
    assert uphill > nominal


def test_arrival_soc_pct() -> None:
    """Verify battery SoC deduction over distance."""
    # 40 kWh battery, 150 Wh/km, 50 km distance = 7.5 kWh consumed = 18.75% SoC drop
    arr_soc = arrival_soc_pct(current_soc_pct=80.0, distance_km=50.0, battery_kwh=40.0, wh_per_km=150.0)
    assert pytest.approx(arr_soc, rel=1e-2) == 80.0 - 18.75


def test_charge_requirements() -> None:
    """Verify charging energy and duration to 80% SoC."""
    # From 30% to 80% on 40 kWh battery = 50% SoC delta = 20 kWh
    # At 50 kW effective power: 20 kWh / 50 kW = 0.4 hours = 24.0 min
    kwh, duration_min = charge_requirements(
        arrival_soc=30.0,
        target_soc=80.0,
        battery_kwh=40.0,
        effective_kw=50.0,
    )
    assert pytest.approx(kwh, rel=1e-5) == 20.0
    assert pytest.approx(duration_min, rel=1e-5) == 24.0

"""Unit tests for CERCOS queue models (Erlang-C and Allen-Cunneen M/G/c).

Verifies analytical models against textbook reference values and physical boundaries.
"""
import math

import pytest
from app.queue.queue import (
    allen_cunneen_mgc_wq,
    erlang_c,
    estimate_station_wait_min,
    mmc_wq,
)


def test_erlang_c_textbook_mm1() -> None:
    """Verify M/M/1 Erlang-C wait probability for lambda=0.5, mu=1.0 (a=0.5)."""
    # For M/M/1: P(wait) = a = 0.5
    p_wait = erlang_c(c=1, a=0.5)
    assert pytest.approx(p_wait, rel=1e-5) == 0.5


def test_mm1_wq_textbook_values() -> None:
    """Verify M/M/1 mean queue wait Wq = 1.0 hour for lambda=0.5, mu=1.0."""
    # Wq = a / (mu - lambda) = 0.5 / (1.0 - 0.5) = 1.0 hour
    wq = mmc_wq(lam=0.5, mu=1.0, c=1)
    assert pytest.approx(wq, rel=1e-5) == 1.0


def test_erlang_c_textbook_mm2() -> None:
    """Verify M/M/2 Erlang-C wait probability for lambda=1.5, mu=1.0 (a=1.5, c=2)."""
    # a = 1.5, c = 2
    # s = 1 + 1.5 = 2.5
    # t = (1.5^2 / 2) * (1 / (1 - 1.5/2)) = (2.25 / 2) * (1 / 0.25) = 1.125 * 4 = 4.5
    # P(wait) = 4.5 / (2.5 + 4.5) = 4.5 / 7.0 = 9 / 14 approx 0.64285714
    p_wait = erlang_c(c=2, a=1.5)
    assert pytest.approx(p_wait, rel=1e-5) == 0.642857


def test_mm2_wq_textbook_values() -> None:
    """Verify M/M/2 mean queue wait Wq = 1.285714 hours for lambda=1.5, mu=1.0, c=2."""
    # Wq = P(wait) / (c*mu - lambda) = (9/14) / (2.0 - 1.5) = (9/14) / 0.5 = 18/14 = 9/7 approx 1.285714 hours
    wq = mmc_wq(lam=1.5, mu=1.0, c=2)
    assert pytest.approx(wq, rel=1e-5) == 1.285714


def test_queue_saturation_boundary() -> None:
    """Verify that offered load a >= c returns saturation values."""
    # When a == c or a > c, queue is unstable
    assert erlang_c(c=2, a=2.0) == 1.0
    assert erlang_c(c=2, a=2.5) == 1.0

    assert math.isinf(mmc_wq(lam=2.0, mu=1.0, c=2))
    assert math.isinf(mmc_wq(lam=3.0, mu=1.0, c=2))
    assert math.isinf(allen_cunneen_mgc_wq(lam=2.0, mu=1.0, c=2))


def test_allen_cunneen_mgc_matches_mmc_when_scv_is_one() -> None:
    """Verify that Allen-Cunneen equals M/M/c exactly when Ca^2=1.0 and Cs^2=1.0."""
    lam, mu, c = 1.2, 1.0, 2
    wq_mmc = mmc_wq(lam=lam, mu=mu, c=c)
    wq_mgc = allen_cunneen_mgc_wq(lam=lam, mu=mu, c=c, ca2=1.0, cs2=1.0)
    assert pytest.approx(wq_mgc, rel=1e-6) == wq_mmc


def test_allen_cunneen_service_time_variance_effect() -> None:
    """Verify that reduced service variance (deterministic charging) reduces queue wait."""
    lam, mu, c = 1.0, 1.0, 2
    wq_exponential = allen_cunneen_mgc_wq(lam=lam, mu=mu, c=c, ca2=1.0, cs2=1.0)
    # Lower SCV (more predictable session duration, e.g. Cs^2 = 0.4)
    wq_low_var = allen_cunneen_mgc_wq(lam=lam, mu=mu, c=c, ca2=1.0, cs2=0.4)
    assert wq_low_var < wq_exponential
    # Higher SCV (wide dispersion, e.g. Cs^2 = 1.6)
    wq_high_var = allen_cunneen_mgc_wq(lam=lam, mu=mu, c=c, ca2=1.0, cs2=1.6)
    assert wq_high_var > wq_exponential


def test_estimate_station_wait_min() -> None:
    """Verify high-level station wait estimator in minutes."""
    # Under low load, wait is small
    wait_low = estimate_station_wait_min(
        station_power_kw=50.0,
        num_connectors=4,
        arrival_rate_per_hour=1.0,
    )
    assert 0.0 <= wait_low <= 15.0

    # Under high load approaching capacity, wait increases
    wait_high = estimate_station_wait_min(
        station_power_kw=30.0,
        num_connectors=2,
        arrival_rate_per_hour=3.8,
    )
    assert wait_high > wait_low


def test_queue_input_validation() -> None:
    """Verify ValueError is raised on invalid queue parameters."""
    with pytest.raises(ValueError):
        erlang_c(c=0, a=1.0)
    with pytest.raises(ValueError):
        erlang_c(c=2, a=-0.5)
    with pytest.raises(ValueError):
        mmc_wq(lam=-1.0, mu=1.0, c=2)
    with pytest.raises(ValueError):
        mmc_wq(lam=1.0, mu=0.0, c=2)
    with pytest.raises(ValueError):
        allen_cunneen_mgc_wq(lam=1.0, mu=1.0, c=2, ca2=-0.1)

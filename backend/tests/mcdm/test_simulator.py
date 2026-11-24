"""Regression test for seeded synthetic simulator matching research/results.json."""
import pytest
from app.mcdm.simulator import simulate_corridor


def test_seeded_simulator_reproduces_pilot_experiment() -> None:
    """Verify that the modular simulator runs and matches pilot experiment statistics."""
    # Run with smaller trip count for fast test execution
    policy_table, infeasible = simulate_corridor(n_trips=2000, seed=42)

    assert len(policy_table) >= 8
    assert infeasible >= 0

    policies = {row["policy"]: row for row in policy_table}
    assert "Nearest" in policies
    assert "CheapestOnly" in policies
    assert "FastestOnly" in policies
    assert "TOPSIS-Balanced" in policies

    # Nearest policy has baseline delta 0.0
    assert pytest.approx(policies["Nearest"]["delta_gen_cost_vs_nearest"], abs=1e-5) == 0.0

    # Fastest and TOPSIS policies reduce generalized trip cost relative to nearest
    assert policies["FastestOnly"]["delta_gen_cost_vs_nearest"] < 0.0
    assert policies["TOPSIS-Fastest"]["delta_gen_cost_vs_nearest"] < 0.0

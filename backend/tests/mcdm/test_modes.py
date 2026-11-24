"""Unit tests for decision mode configuration, weights summation, and segment overrides."""
import numpy as np
import pytest
from app.mcdm.modes import (
    get_weights_for_mode,
    load_all_mode_weights,
    load_criteria_bounds,
)


def test_all_mode_weights_sum_to_one() -> None:
    """Verify that criteria weights sum to 1.0 within tolerance for every decision mode."""
    all_weights = load_all_mode_weights()
    assert len(all_weights) == 6

    for mode, w in all_weights.items():
        assert len(w) == 6, f"Mode {mode} must have exactly 6 criteria weights"
        assert pytest.approx(w.sum(), rel=1e-5) == 1.0, f"Mode {mode} weights must sum to 1.0"
        assert all(val >= 0.0 for val in w), f"Weights for mode {mode} must be non-negative"


def test_criteria_bounds_shape_and_order() -> None:
    """Verify criteria bounds load a valid (6, 2) array with low < high."""
    bounds = load_criteria_bounds()
    assert bounds.shape == (6, 2)
    # Every criterion must have lower_bound < upper_bound
    for i in range(6):
        assert bounds[i, 0] < bounds[i, 1]


def test_get_weights_for_mode_fallback() -> None:
    """Verify fallback to Balanced mode when an unknown mode name is requested."""
    w_unknown = get_weights_for_mode("NonExistentMode")
    w_balanced = get_weights_for_mode("Balanced")
    np.testing.assert_array_almost_equal(w_unknown, w_balanced)


def test_segment_specific_mode_overrides() -> None:
    """Verify segment override loading (defaults retained when override is empty)."""
    # Segment overrides in config/weights.yaml are currently empty pending Kashish's survey
    w_e2w = get_weights_for_mode("Cheapest", segment="E2W")
    w_default = get_weights_for_mode("Cheapest")
    np.testing.assert_array_almost_equal(w_e2w, w_default)

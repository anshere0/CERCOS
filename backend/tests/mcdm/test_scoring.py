"""Unit tests for anchored WSM scoring and TOPSIS baseline."""
import numpy as np
import pytest
from app.mcdm.criteria import BENEFIT_VECTOR
from app.mcdm.modes import DEFAULT_MODE_WEIGHTS, load_criteria_bounds
from app.mcdm.topsis import topsis
from app.mcdm.wsm_anchored import wsm_anchored


def test_anchored_wsm_ideal_alternative_scores_one() -> None:
    """Verify that an alternative achieving the best bound on all criteria scores exactly 1.0."""
    bounds = load_criteria_bounds()

    # Construct the ideal alternative:
    # Cost criteria (detour, cost, wait) at minimum bound
    # Benefit criteria (speed, rating, arrival SoC) at maximum bound
    ideal_row = np.array([
        bounds[0, 0],  # detour_km = 0.0
        bounds[1, 0],  # cost = 8.0
        bounds[2, 0],  # wait = 0.0
        bounds[3, 1],  # speed = 60.0
        bounds[4, 1],  # rating = 5.0
        bounds[5, 1],  # SoC = 100.0
    ]).reshape(1, -1)

    weights = np.array(DEFAULT_MODE_WEIGHTS["Balanced"])
    score = wsm_anchored(ideal_row, weights, bounds, BENEFIT_VECTOR)
    assert pytest.approx(score[0], rel=1e-5) == 1.0


def test_anchored_wsm_worst_alternative_scores_zero() -> None:
    """Verify that an alternative achieving the worst bound on all criteria scores 0.0."""
    bounds = load_criteria_bounds()

    worst_row = np.array([
        bounds[0, 1],  # detour_km = 10.0 (worst)
        bounds[1, 1],  # cost = 28.0 (worst)
        bounds[2, 1],  # wait = 60.0 (worst)
        bounds[3, 0],  # speed = 3.3 (worst)
        bounds[4, 0],  # rating = 1.0 (worst)
        bounds[5, 0],  # SoC = 0.0 (worst)
    ]).reshape(1, -1)

    weights = np.array(DEFAULT_MODE_WEIGHTS["Balanced"])
    score = wsm_anchored(worst_row, weights, bounds, BENEFIT_VECTOR)
    assert pytest.approx(score[0], rel=1e-5) == 0.0


def test_dominated_alternative_never_ranks_first() -> None:
    """Verify that a strictly dominated alternative never outranks a dominant candidate."""
    bounds = load_criteria_bounds()
    weights = np.array(DEFAULT_MODE_WEIGHTS["Balanced"])

    # Superior candidate vs inferior dominated candidate
    dominant = [1.0, 12.0, 5.0, 50.0, 4.5, 40.0]
    dominated = [5.0, 22.0, 30.0, 15.0, 3.0, 15.0]

    X = np.array([dominant, dominated])
    scores = wsm_anchored(X, weights, bounds, BENEFIT_VECTOR)

    assert scores[0] > scores[1]
    assert np.argmax(scores) == 0


def test_topsis_baseline_runs() -> None:
    """Verify classic vector-norm TOPSIS computes valid relative closeness."""
    weights = np.array(DEFAULT_MODE_WEIGHTS["Balanced"])
    X = np.array([
        [1.0, 12.0, 5.0, 50.0, 4.5, 40.0],
        [3.0, 18.0, 15.0, 30.0, 4.0, 30.0],
    ])
    closeness = topsis(X, weights, BENEFIT_VECTOR)
    assert len(closeness) == 2
    assert 0.0 <= closeness[0] <= 1.0
    assert 0.0 <= closeness[1] <= 1.0
    assert closeness[0] > closeness[1]

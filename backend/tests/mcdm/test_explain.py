"""Unit tests for recommendation explainability and per-criterion contribution accounting."""
from app.mcdm.explain import explain_candidate_score


def test_explain_candidate_score_structure() -> None:
    """Verify explain output generates contributions and human-readable notes."""
    crit_vals = {
        "detour_km": 0.8,
        "cost_inr_per_kwh": 14.5,
        "wait_min": 5.0,
        "effective_kw": 50.0,
        "rating": 4.5,
        "arrival_soc_pct": 32.0,
    }
    norm_vals = {
        "detour_km": 0.92,
        "cost_inr_per_kwh": 0.675,
        "wait_min": 0.916,
        "effective_kw": 0.823,
        "rating": 0.875,
        "arrival_soc_pct": 0.32,
    }
    weights = [0.20, 0.20, 0.20, 0.15, 0.10, 0.15]

    explanations = explain_candidate_score(
        criteria_values=crit_vals,
        normalized_values=norm_vals,
        weights=weights,
        mode="Balanced",
    )

    assert len(explanations) == 6
    for item in explanations:
        assert "criterion" in item
        assert "contribution" in item
        assert "note" in item
        assert item["contribution"] >= 0.0

    # Ensure notes are non-empty
    notes = [e["note"] for e in explanations]
    assert all(len(n) > 5 for n in notes)

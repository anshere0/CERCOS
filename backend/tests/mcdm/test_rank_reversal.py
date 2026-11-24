"""Statistical validation test for rank reversal across 4,000 randomized problems.

Verifies the foundational mathematical property of CERCOS MCDM:
Anchored WSM achieves strictly 0.0% rank reversal under candidate addition/deletion,
whereas vector-normalized TOPSIS and min-max WSM exhibit noticeable rank reversal.
"""
from app.mcdm.simulator import simulate_rank_reversals


def test_anchored_wsm_zero_rank_reversal_on_4000_problems() -> None:
    """Formally test that anchored scoring exhibits strictly ZERO rank reversals over 4,000 problems."""
    results = simulate_rank_reversals(n_problems=4000, seed=42)

    # Anchored scoring MUST have 0 rank reversals
    assert results["WSM (anchored bounds)"] == 0, (
        f"Anchored scoring must have zero rank reversals, got {results['WSM (anchored bounds)']}"
    )

    # Relative methods (TOPSIS and Min-Max) are expected to suffer rank reversals
    assert results["TOPSIS (vector norm)"] > 0, "Vector-norm TOPSIS should show rank reversals"
    assert results["WSM (min-max)"] > 0, "Min-Max WSM should show rank reversals"

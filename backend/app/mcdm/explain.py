"""Decision explainability and contribution accounting for CERCOS recommendations.

Breaks down candidate scores into per-criterion contribution points:
    contribution_j = weight_j * normalized_score_j
and generates qualitative human-readable reasoning notes for the UI.
"""
from typing import Any

from app.mcdm.criteria import CRITERIA_NAMES


def explain_candidate_score(
    criteria_values: dict[str, float],
    normalized_values: dict[str, float],
    weights: list[float] | dict[str, float],
    mode: str,
) -> list[dict[str, Any]]:
    """Generate per-criterion contribution breakdown and qualitative explanation notes.

    Parameters
    ----------
    criteria_values : dict[str, float]
        Raw criterion values (e.g., detour_km=1.2, cost_inr_kwh=14.0).
    normalized_values : dict[str, float]
        Normalized criterion values in [0, 1].
    weights : list[float] | dict[str, float]
        Mode criteria weights.
    mode : str
        Selected decision mode (e.g. "Cheapest", "Fastest").

    Returns
    -------
    list[dict[str, Any]]
        List of dicts formatted matching CriterionExplain schema:
        [{"criterion": str, "contribution": float, "note": str}]
    """
    if isinstance(weights, list):
        w_dict = {name: weights[i] for i, name in enumerate(CRITERIA_NAMES)}
    else:
        w_dict = weights

    explanations: list[dict[str, Any]] = []

    for crit in CRITERIA_NAMES:
        w = float(w_dict.get(crit, 0.0))
        norm = float(normalized_values.get(crit, 0.0))
        contrib = round(w * norm, 3)
        raw_val = float(criteria_values.get(crit, 0.0))

        note = ""
        if crit == "effective_kw":
            note = f"Effective power capped at {raw_val} kW for vehicle acceptance"
        elif crit == "cost_inr_per_kwh":
            note = f"Tariff of ₹{raw_val:.2f}/kWh"
        elif crit == "detour_km":
            note = f"{raw_val:.1f} km highway detour from direct path"
        elif crit == "wait_min":
            note = f"Estimated queue wait of {raw_val:.1f} min"
        elif crit == "rating":
            note = f"User feedback rating of {raw_val:.1f}/5.0"
        elif crit == "arrival_soc_pct":
            note = f"Safe arrival SoC of {raw_val:.1f}% (>8% safety reserve)"

        explanations.append({
            "criterion": crit,
            "contribution": contrib,
            "note": note,
        })

    # Sort descending by contribution so the primary drivers appear first in the UI
    explanations.sort(key=lambda x: x["contribution"], reverse=True)
    return explanations

"""CERCOS Multi-Criteria Decision Making (MCDM) Recommendation Engine Package.

Provides deterministic charging stop recommendation, domain-anchored WSM scoring,
TOPSIS comparison baselines, range models, and simulation tools.
"""
from app.mcdm.criteria import (
    BENEFIT_VECTOR,
    CRITERIA_NAMES,
    effective_charging_power,
    filter_and_evaluate_candidates,
)
from app.mcdm.explain import explain_candidate_score
from app.mcdm.modes import (
    get_weights_for_mode,
    load_all_mode_weights,
    load_criteria_bounds,
)
from app.mcdm.range import (
    arrival_soc_pct,
    charge_requirements,
    effective_wh_per_km,
    reachable_distance_km,
    usable_energy_kwh,
)
from app.mcdm.recommend import ENGINE_VERSION, recommend
from app.mcdm.topsis import topsis, wsm_minmax
from app.mcdm.wsm_anchored import normalize_anchored, wsm_anchored

__all__ = [
    "BENEFIT_VECTOR",
    "CRITERIA_NAMES",
    "ENGINE_VERSION",
    "arrival_soc_pct",
    "charge_requirements",
    "effective_charging_power",
    "effective_wh_per_km",
    "explain_candidate_score",
    "filter_and_evaluate_candidates",
    "get_weights_for_mode",
    "load_all_mode_weights",
    "load_criteria_bounds",
    "normalize_anchored",
    "reachable_distance_km",
    "recommend",
    "topsis",
    "usable_energy_kwh",
    "wsm_anchored",
    "wsm_minmax",
]

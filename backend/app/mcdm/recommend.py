"""Deterministic charging stop recommendation engine for CERCOS.

Implements pure function `recommend()` conforming to `contracts/engine_interface.md`
and `app.schemas.recommend`:
    recommend(request, stations, vehicle, weights=None, bounds=None) -> RecommendResult

Enforces:
1. 8.0% mandatory battery safety reserve.
2. Hard candidate rejection (unoperational, connector mismatch, unreachable).
3. Physical bottleneck law: P_eff = min(P_station, P_vehicle).
4. Anchored WSM scoring with zero rank reversal.
5. Deterministic, fully audited outputs.
"""
from typing import Any

import numpy as np

from app.mcdm.criteria import (
    CRITERIA_NAMES,
    filter_and_evaluate_candidates,
)
from app.mcdm.explain import explain_candidate_score
from app.mcdm.modes import (
    get_weights_for_mode,
    load_criteria_bounds,
)
from app.mcdm.range import (
    effective_wh_per_km,
    reachable_distance_km,
)
from app.mcdm.wsm_anchored import normalize_anchored, wsm_anchored
from app.schemas.recommend import (
    CriteriaValues,
    CriterionExplain,
    RecommendRequest,
    RecommendResult,
    RejectedStation,
    TopStationResult,
)

ENGINE_VERSION: str = "0.2.0-mcdm"


def recommend(
    request: RecommendRequest | dict[str, Any],
    stations: list[dict[str, Any]],
    vehicle: dict[str, Any],
    weights: list[float] | np.ndarray | None = None,
    bounds: np.ndarray | None = None,
) -> RecommendResult:
    """Recommend optimal EV charging stops along a travel route.

    Parameters
    ----------
    request : RecommendRequest | dict
        Recommendation request parameters (origin, destination, soc_pct, mode, segment, route_km).
    stations : list[dict]
        Candidate stations to evaluate.
    vehicle : dict
        Vehicle technical specifications (battery_kwh, wh_per_km, max_dc_kw, max_ac_kw, connector_types).
    weights : list[float] | np.ndarray | None
        Optional custom criteria weight vector. If None, loaded from config for mode and segment.
    bounds : np.ndarray | None
        Optional custom criteria bounds. If None, loaded from config/criteria_bounds.yaml.

    Returns
    -------
    RecommendResult
        Pydantic response model containing needs_charging, reachable_km, top3 ranked stops,
        rejected stations with reasons, warnings, and engine_version.
    """
    # 1. Parse request parameters
    if hasattr(request, "model_dump"):
        req_dict = request.model_dump()
    elif hasattr(request, "dict"):
        req_dict = request.dict()
    else:
        req_dict = dict(request)

    mode = str(req_dict.get("mode", "Balanced"))
    segment = str(req_dict.get("segment", vehicle.get("segment", "E4W")))
    soc_pct = float(req_dict.get("soc_pct", 50.0))

    # 2. Extract vehicle parameters and consumption
    battery_kwh = float(vehicle.get("battery_kwh", 40.0))
    base_wh_km = float(vehicle.get("wh_per_km", 150.0))
    wh_km = effective_wh_per_km(base_wh_per_km=base_wh_km)

    # 3. Compute reachable distance with 8% reserve
    reachable_km = reachable_distance_km(
        battery_kwh=battery_kwh,
        current_soc_pct=soc_pct,
        wh_per_km=wh_km,
        reserve_soc_pct=8.0,
    )

    # Route distance (fallback to haversine if route_km not provided)
    route_km = req_dict.get("route_km")
    warnings: list[str] = []
    if route_km is None:
        orig = req_dict.get("origin", {})
        dest = req_dict.get("destination", {})
        # Simple planar/haversine approximation if coordinates provided
        if orig and dest:
            lat1, lon1 = float(orig.get("lat", 0)), float(orig.get("lon", 0))
            lat2, lon2 = float(dest.get("lat", 0)), float(dest.get("lon", 0))
            dlat = np.radians(lat2 - lat1)
            dlon = np.radians(lon2 - lon1)
            a = np.sin(dlat / 2) ** 2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2) ** 2
            c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
            direct_km = 6371.0 * c * 1.3  # 1.3 road curvature factor
            route_km = round(direct_km, 1)
            warnings.append("routing fallback: haversine x1.3")
        else:
            route_km = 100.0

    needs_charging = bool(route_km > reachable_km)

    # 4. Load bounds and weights
    if bounds is None:
        bounds_arr = load_criteria_bounds()
    else:
        bounds_arr = np.asarray(bounds, dtype=float)

    if weights is None:
        weights_arr = get_weights_for_mode(mode=mode, segment=segment)
    else:
        weights_arr = np.asarray(weights, dtype=float)

    # 5. Filter candidates and construct decision matrix
    X, admissible, rejected_list = filter_and_evaluate_candidates(
        stations=stations,
        vehicle=vehicle,
        direct_route_km=float(route_km),
        current_soc_pct=soc_pct,
        wh_per_km=wh_km,
    )

    rejected_models = [RejectedStation(station_id=r["station_id"], reason=r["reason"]) for r in rejected_list]

    # Check for synthetic data presence in stations
    if any(s.get("source") == "synthetic" for s in stations):
        warnings.append("synthetic data used")

    # 6. Score admissible candidates
    top3: list[TopStationResult] = []
    if len(admissible) > 0 and X.shape[0] > 0:
        scores = wsm_anchored(X, weights_arr, bounds_arr)
        norm_matrix = normalize_anchored(X, bounds_arr)

        scored_candidates: list[dict[str, Any]] = []
        for i, cand in enumerate(admissible):
            crit_dict = {
                CRITERIA_NAMES[j]: float(X[i, j]) for j in range(len(CRITERIA_NAMES))
            }
            norm_dict = {
                CRITERIA_NAMES[j]: float(norm_matrix[i, j]) for j in range(len(CRITERIA_NAMES))
            }

            explain_list = explain_candidate_score(
                criteria_values=crit_dict,
                normalized_values=norm_dict,
                weights=weights_arr.tolist(),
                mode=mode,
            )

            cand_score = float(round(scores[i], 4))
            cand_data = {
                "station_id": cand["station_id"],
                "name": cand["name"],
                "score": cand_score,
                "eta_extra_min": cand["eta_extra_min"],
                "est_cost_inr": cand["est_cost_inr"],
                "est_charge_min": cand["est_charge_min"],
                "arrival_soc_pct": cand["arrival_soc_pct"],
                "criteria": CriteriaValues(
                    detour_km=crit_dict["detour_km"],
                    cost_inr_kwh=crit_dict["cost_inr_per_kwh"],
                    wait_min=crit_dict["wait_min"],
                    effective_kw=crit_dict["effective_kw"],
                    rating=crit_dict["rating"],
                    arrival_soc_pct=crit_dict["arrival_soc_pct"],
                ),
                "explain": [CriterionExplain(**e) for e in explain_list],
                "source": cand["source"],
                "confidence": cand["confidence"],
            }
            scored_candidates.append(cand_data)

        # Sort descending by composite score
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)

        # Assign ranks to top 3
        for rank_idx, cand_info in enumerate(scored_candidates[:3], start=1):
            cand_info["rank"] = rank_idx
            top3.append(TopStationResult(**cand_info))

    return RecommendResult(
        needs_charging=needs_charging,
        reachable_km=reachable_km,
        top3=top3,
        rejected=rejected_models,
        warnings=warnings,
        engine_version=ENGINE_VERSION,
    )

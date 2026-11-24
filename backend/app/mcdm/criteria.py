"""Decision criteria and candidate evaluation filters for CERCOS.

Implements:
1. Physical charging power bottleneck:
       P_eff = min(P_station, P_vehicle)
2. Hard rejection filters:
       - Station operational check
       - Connector compatibility check
       - Arrival SoC >= 8.0% reserve reachability check
3. Multi-criteria decision matrix formulation for [detour, cost, wait, speed, rating, safety].
"""
from typing import Any

import numpy as np

from app.mcdm.range import arrival_soc_pct, charge_requirements

# Criteria definition matching config/weights.yaml and PROJECT_MANIFEST.yaml
CRITERIA_NAMES: list[str] = [
    "detour_km",
    "cost_inr_per_kwh",
    "wait_min",
    "effective_kw",
    "rating",
    "arrival_soc_pct",
]

# Benefit vector: True for benefit criteria (higher is better), False for cost criteria (lower is better)
# detour_km (cost=0), cost_inr_per_kwh (cost=0), wait_min (cost=0),
# effective_kw (benefit=1), rating (benefit=1), arrival_soc_pct (benefit=1)
BENEFIT_VECTOR: np.ndarray = np.array([False, False, False, True, True, True], dtype=bool)


def effective_charging_power(
    station_power_kw: float,
    vehicle_max_dc_kw: float | None,
    vehicle_max_ac_kw: float | None,
    compatible_connectors: list[str] | set[str],
) -> float:
    """Enforce the fundamental CERCOS physical charging power bottleneck.

    Speed criterion = min(station_kW, vehicle_max_accept_kW) — never raw station kW.

    Parameters
    ----------
    station_power_kw : float
        Maximum output power capability of the station connector in kW.
    vehicle_max_dc_kw : float | None
        Vehicle maximum DC fast charging acceptance power in kW.
    vehicle_max_ac_kw : float | None
        Vehicle maximum AC onboard charger acceptance power in kW.
    compatible_connectors : list[str] | set[str]
        Compatible connector types between station and vehicle.

    Returns
    -------
    float
        Effective charging power in kW.
    """
    dc_types = {"CCS2", "GB/T", "CHAdeMO", "Bharat_DC001"}
    has_dc = any(c in dc_types for c in compatible_connectors)

    if has_dc and vehicle_max_dc_kw is not None and vehicle_max_dc_kw > 0:
        veh_limit = vehicle_max_dc_kw
    else:
        veh_limit = vehicle_max_ac_kw if (vehicle_max_ac_kw is not None and vehicle_max_ac_kw > 0) else 3.3

    return float(round(min(station_power_kw, veh_limit), 2))


def filter_and_evaluate_candidates(
    stations: list[dict[str, Any]],
    vehicle: dict[str, Any],
    direct_route_km: float,
    current_soc_pct: float,
    wh_per_km: float,
    avg_speed_kmh: float = 45.0,
    target_charge_soc_pct: float = 80.0,
) -> tuple[np.ndarray, list[dict[str, Any]], list[dict[str, Any]]]:
    """Filter candidate stations and construct the decision matrix.

    Parameters
    ----------
    stations : list[dict]
        Candidate stations from database or seed fixtures.
    vehicle : dict
        Vehicle specifications (battery_kwh, wh_per_km, max_dc_kw, max_ac_kw, connector_types).
    direct_route_km : float
        Nominal distance from origin to destination without detours.
    current_soc_pct : float
        Current vehicle battery state of charge.
    wh_per_km : float
        Vehicle energy consumption rate.
    avg_speed_kmh : float
        Estimated detour travel speed.
    target_charge_soc_pct : float
        Target charging state of charge (default 80%).

    Returns
    -------
    tuple[np.ndarray, list[dict], list[dict]]
        - X : numpy array of shape (N_admissible, 6) containing the raw decision matrix.
        - admissible_candidates : list of evaluated station metadata dictionaries.
        - rejected_candidates : list of dicts with {"station_id": int, "reason": str}.
    """
    battery_kwh = float(vehicle.get("battery_kwh", 40.0))
    vehicle_connectors = set(vehicle.get("connector_types", []))
    max_dc_kw = vehicle.get("max_dc_kw")
    max_ac_kw = vehicle.get("max_ac_kw")

    admissible_candidates: list[dict[str, Any]] = []
    rejected_candidates: list[dict[str, Any]] = []
    matrix_rows: list[list[float]] = []

    for s in stations:
        station_id = int(s.get("station_id", 0))
        station_name = s.get("name", s.get("station_name", f"Station {station_id}"))

        # 1. Operational filter
        if not s.get("is_operational", True):
            rejected_candidates.append({
                "station_id": station_id,
                "reason": "Station temporarily out of service",
            })
            continue

        # 2. Connector compatibility filter
        station_connectors = s.get("connector_types", [])
        if not station_connectors and "connectors" in s:
            station_connectors = [c.get("connector_type") for c in s["connectors"] if isinstance(c, dict)]

        matched_connectors = set(station_connectors).intersection(vehicle_connectors)
        if not matched_connectors:
            rejected_candidates.append({
                "station_id": station_id,
                "reason": f"Connector mismatch: vehicle requires {sorted(vehicle_connectors)}, station has {sorted(station_connectors)}",
            })
            continue

        # 3. Distance and reachability calculation
        detour_km = float(s.get("detour_km", 0.0))
        km_along_route = float(s.get("km_along_route", direct_route_km * 0.5))
        dist_to_station_km = km_along_route + detour_km

        arr_soc = arrival_soc_pct(
            current_soc_pct=current_soc_pct,
            distance_km=dist_to_station_km,
            battery_kwh=battery_kwh,
            wh_per_km=wh_per_km,
        )

        if arr_soc < 8.0:
            rejected_candidates.append({
                "station_id": station_id,
                "reason": f"Unreachable: arrival SoC {arr_soc:.1f}% is below 8.0% safety reserve",
            })
            continue

        # 4. Physical power bottleneck
        st_power_kw = float(s.get("max_power_kw", 22.0))
        eff_kw = effective_charging_power(
            station_power_kw=st_power_kw,
            vehicle_max_dc_kw=max_dc_kw,
            vehicle_max_ac_kw=max_ac_kw,
            compatible_connectors=matched_connectors,
        )

        # 5. Charging duration and cost estimation
        kwh_to_charge, charge_min = charge_requirements(
            arrival_soc=arr_soc,
            target_soc=target_charge_soc_pct,
            battery_kwh=battery_kwh,
            effective_kw=eff_kw,
        )

        tariff = float(s.get("tariff_inr_kwh", s.get("tariff", 18.0)))
        est_cost_inr = round(kwh_to_charge * tariff, 2)
        predicted_wait = float(s.get("predicted_wait_min", s.get("wait_min", 5.0)))
        rating = float(s.get("rating", 4.0))

        # ETA extra = travel detour time + wait + charging duration
        detour_travel_min = (detour_km / avg_speed_kmh) * 60.0
        eta_extra_min = round(detour_travel_min + predicted_wait + charge_min, 1)

        # Raw criterion values matching CRITERIA_NAMES:
        # [detour_km, cost_inr_per_kwh, wait_min, effective_kw, rating, arrival_soc_pct]
        row = [
            round(detour_km, 2),
            round(tariff, 2),
            round(predicted_wait, 1),
            round(eff_kw, 2),
            round(rating, 2),
            round(arr_soc, 2),
        ]
        matrix_rows.append(row)

        admissible_candidates.append({
            "station_id": station_id,
            "name": station_name,
            "detour_km": detour_km,
            "cost_inr_kwh": tariff,
            "wait_min": predicted_wait,
            "effective_kw": eff_kw,
            "rating": rating,
            "arrival_soc_pct": arr_soc,
            "eta_extra_min": eta_extra_min,
            "est_cost_inr": est_cost_inr,
            "est_charge_min": charge_min,
            "source": s.get("source", "osm"),
            "confidence": float(s.get("confidence", 0.90)),
        })

    if matrix_rows:
        X = np.array(matrix_rows, dtype=float)
    else:
        X = np.empty((0, len(CRITERIA_NAMES)), dtype=float)

    return X, admissible_candidates, rejected_candidates

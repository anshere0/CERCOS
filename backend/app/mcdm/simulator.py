"""Seeded synthetic simulator and rank-reversal validation module for CERCOS.

Encapsulates research simulation experiments from research/01_cercos_pilot_experiments.py
into reusable, testable Python functions.

Validation Targets:
1. Replicates research/results.json corridor simulation metrics within statistical confidence.
2. Formally measures and verifies rank reversal rates across 4,000 randomized decision problems:
   - TOPSIS (vector norm): non-zero rank reversals
   - WSM (min-max): non-zero rank reversals
   - WSM (anchored bounds): strictly 0.0% rank reversals
"""
import math
from typing import Any

import numpy as np

from app.mcdm.criteria import BENEFIT_VECTOR
from app.mcdm.topsis import topsis, wsm_minmax
from app.mcdm.wsm_anchored import wsm_anchored
from app.queue.queue import erlang_c, mmc_wq

SIMULATOR_MODES: dict[str, list[float]] = {
    "Cheapest": [0.10, 0.50, 0.10, 0.10, 0.05, 0.15],
    "Fastest": [0.10, 0.05, 0.25, 0.45, 0.05, 0.10],
    "Shortest": [0.45, 0.05, 0.25, 0.10, 0.05, 0.10],
    "HighestRated": [0.10, 0.10, 0.10, 0.10, 0.50, 0.10],
    "BatterySafe": [0.10, 0.05, 0.05, 0.10, 0.05, 0.65],
    "Balanced": [0.20, 0.20, 0.20, 0.15, 0.10, 0.15],
}

DEFAULT_SIM_BOUNDS = np.array([
    [0.0, 10.0],   # detour_km
    [8.0, 28.0],   # cost_inr_per_kwh
    [0.0, 60.0],   # wait_min
    [3.3, 60.0],   # effective_kw
    [1.0, 5.0],    # rating
    [0.0, 100.0],  # arrival_soc_pct
], dtype=float)


def simulate_corridor(
    n_trips: int = 20000,
    seed: int = 42,
    corridor_length_km: float = 180.0,
    n_stations: int = 10,
    vot_inr_h: float = 120.0,
) -> tuple[list[dict[str, Any]], int]:
    """Run seeded synthetic corridor simulation comparing EV charging routing policies.

    Parameters
    ----------
    n_trips : int
        Number of simulated trips (default 20,000).
    seed : int
        Random seed for reproducibility.
    corridor_length_km : float
        Corridor distance in km.
    n_stations : int
        Number of candidate stations along corridor.
    vot_inr_h : float
        Value of Time in INR/hour (default 120 Rs/h).

    Returns
    -------
    tuple[list[dict], int]
        - policy_table : List of performance metrics per policy (Nearest, Cheapest, Fastest, TOPSIS-*).
        - infeasible_trips : Count of trips where vehicle initial SoC could not reach any station.
    """
    rng = np.random.default_rng(seed)

    cap_kwh = 40.0
    cons_base = 0.150  # kWh/km
    v_accept_kw = 50.0
    speed_detour = 40.0

    res: dict[str, list[tuple[float, float, float, float, float]]] = {
        k: [] for k in ["Nearest", "CheapestOnly", "FastestOnly"] + [f"TOPSIS-{m}" for m in SIMULATOR_MODES]
    }
    infeasible = 0

    for _ in range(n_trips):
        # Corridor station generator
        pos = np.sort(rng.uniform(5, corridor_length_km - 5, n_stations))
        detour = rng.uniform(0.2, 6.0, n_stations)
        power = rng.choice([7.4, 25.0, 30.0, 60.0, 120.0], n_stations, p=[0.25, 0.20, 0.20, 0.25, 0.10])
        tariff = np.clip(10.0 + 0.07 * power + rng.normal(0, 2.5, n_stations), 9.0, 26.0)
        rating = np.clip(rng.normal(3.9, 0.5, n_stations), 2.5, 4.9)
        conn = rng.integers(2, 7, n_stations)
        rho = rng.uniform(0.15, 0.90, n_stations)

        soc0 = rng.uniform(0.15, 0.45)
        cons_true = cons_base * rng.normal(1.0, 0.12)
        e0 = soc0 * cap_kwh
        reach_pred = (e0 - 0.08 * cap_kwh) / cons_base

        ok = np.where(pos + detour <= reach_pred)[0]
        if len(ok) == 0:
            infeasible += 1
            continue

        eff_p = np.minimum(power, v_accept_kw)
        mu = 1.0 / ((0.35 * cap_kwh) / eff_p)  # sessions/h per connector
        lam = rho * conn * mu
        wq_true = np.array([mmc_wq(l, m, c) for l, m, c in zip(lam, mu, conn)]) * 60.0
        wq_pred = wq_true * rng.lognormal(0, 0.35, n_stations)
        arr_soc_pred = (e0 - (pos + detour) * cons_base) / cap_kwh * 100.0

        # Decision matrix over reachable stations: [detour, cost, wait, speed, rating, safety]
        X = np.c_[detour, tariff, wq_pred, eff_p, rating, arr_soc_pred][ok]

        choices = {
            "Nearest": ok[np.argmin(pos[ok] + detour[ok])],
            "CheapestOnly": ok[np.argmin(tariff[ok])],
            "FastestOnly": ok[np.argmax(eff_p[ok])],
        }
        for m, w in SIMULATOR_MODES.items():
            choices[f"TOPSIS-{m}"] = ok[np.argmax(topsis(X, np.array(w)))]

        for name, i in choices.items():
            e_arr = e0 - (pos[i] + detour[i]) * cons_true
            stranded = float(e_arr < 0.02 * cap_kwh)
            rem = corridor_length_km - pos[i]
            need = max(0.0, rem * cons_true * 1.10 + 0.10 * cap_kwh - max(e_arr, 0.0))
            need = min(need, 0.8 * cap_kwh - max(e_arr, 0.0)) if need > 0.8 * cap_kwh - max(e_arr, 0.0) else need

            wait = (
                rng.exponential(1.0 / max((conn[i] * mu[i] - lam[i]), 1e-6)) * 60.0
                if rng.random() < erlang_c(conn[i], lam[i] / mu[i])
                else 0.0
            )
            t_ch = (need / eff_p[i]) * 60.0
            t_det = (2.0 * detour[i] / speed_detour) * 60.0
            total_time = wait + t_ch + t_det
            cost = need * tariff[i]
            gen_cost = cost + (total_time / 60.0) * vot_inr_h

            res[name].append((total_time, cost, wait, stranded, gen_cost))

    # Compile summary statistics
    res_arr = {k: np.array(v) for k, v in res.items()}
    base = res_arr["Nearest"]
    rows: list[dict[str, Any]] = []

    for k, a in res_arr.items():
        d = a[:, 4] - base[:, 4]
        se = float(d.std(ddof=1) / math.sqrt(len(d)))
        rows.append({
            "policy": k,
            "mean_time_min": float(a[:, 0].mean()),
            "p90_time_min": float(np.percentile(a[:, 0], 90)),
            "mean_cost_inr": float(a[:, 1].mean()),
            "mean_wait_min": float(a[:, 2].mean()),
            "stranding_pct": float(100.0 * a[:, 3].mean()),
            "gen_cost_inr": float(a[:, 4].mean()),
            "delta_gen_cost_vs_nearest": float(d.mean()),
            "ci95": float(1.96 * se),
        })

    return rows, infeasible


def simulate_rank_reversals(
    n_problems: int = 4000,
    seed: int = 42,
    m_candidates: int = 6,
) -> dict[str, int]:
    """Test rank stability when an irrelevant alternative is added or removed.

    Evaluates across:
    1. TOPSIS (vector norm)
    2. WSM (min-max normalization)
    3. WSM (anchored bounds)

    Returns
    -------
    dict[str, int]
        Count of rank reversals observed across n_problems.
    """
    rng = np.random.default_rng(seed)
    weights = np.array(SIMULATOR_MODES["Balanced"])
    bounds = DEFAULT_SIM_BOUNDS

    rev_counts = {
        "TOPSIS (vector norm)": 0,
        "WSM (min-max)": 0,
        "WSM (anchored bounds)": 0,
    }

    for _ in range(n_problems):
        # Generate random candidate matrix of shape (m, 6)
        # [detour, tariff, wait, power, rating, arr_soc]
        X = np.c_[
            rng.uniform(0.2, 8.0, m_candidates),
            rng.uniform(9.0, 26.0, m_candidates),
            rng.uniform(0.0, 40.0, m_candidates),
            rng.choice([7.4, 25.0, 30.0, 50.0], m_candidates),
            rng.uniform(2.5, 4.9, m_candidates),
            rng.uniform(3.0, 45.0, m_candidates),
        ]

        # Calculate initial rankings
        top_idx_topsis = int(np.argmax(topsis(X, weights, BENEFIT_VECTOR)))
        top_idx_minmax = int(np.argmax(wsm_minmax(X, weights, BENEFIT_VECTOR)))
        top_idx_anchored = int(np.argmax(wsm_anchored(X, weights, bounds, BENEFIT_VECTOR)))

        # Introduce a decoy candidate that is strictly dominated by the winner
        # to test if adding an irrelevant alternative flips the winner among existing candidates
        decoy = np.array([
            rng.uniform(7.0, 9.5),   # poor detour (high)
            rng.uniform(24.0, 27.5), # high tariff
            rng.uniform(35.0, 55.0), # high wait
            7.4,                     # low power
            2.0,                     # low rating
            rng.uniform(1.0, 5.0),   # low SoC
        ])
        X_extended = np.vstack([X, decoy])

        new_top_topsis = int(np.argmax(topsis(X_extended, weights, BENEFIT_VECTOR)))
        new_top_minmax = int(np.argmax(wsm_minmax(X_extended, weights, BENEFIT_VECTOR)))
        new_top_anchored = int(np.argmax(wsm_anchored(X_extended, weights, bounds, BENEFIT_VECTOR)))

        if new_top_topsis != top_idx_topsis and new_top_topsis < m_candidates:
            rev_counts["TOPSIS (vector norm)"] += 1

        if new_top_minmax != top_idx_minmax and new_top_minmax < m_candidates:
            rev_counts["WSM (min-max)"] += 1

        if new_top_anchored != top_idx_anchored and new_top_anchored < m_candidates:
            rev_counts["WSM (anchored bounds)"] += 1

    return rev_counts

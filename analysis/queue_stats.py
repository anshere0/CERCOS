"""Empirical queueing statistics extractor (lambda, mu, rho, SCV) from station intervals."""
from typing import Any

import numpy as np


def compute_queue_parameters(
    observations: list[dict[str, Any]],
    num_connectors: int = 2,
) -> dict[str, float]:
    """Compute arrival rate lambda (/hr), service rate mu (/hr), utilization rho, and SCV."""
    if not observations:
        return {"lambda_per_hr": 0.0, "mu_per_hr": 1.0, "rho": 0.0, "ca2": 1.0, "cs2": 1.0}

    arrival_rates: list[float] = []
    service_durations_hr: list[float] = []

    for obs in observations:
        mins = float(obs.get("interval_minutes") or 15.0)
        arrivals = float(obs.get("arrivals_in_interval") or 0.0)
        arrival_rates.append((arrivals / mins) * 60.0)

        if obs.get("service_minutes"):
            service_durations_hr.append(float(obs["service_minutes"]) / 60.0)

    arr_arr = np.asarray(arrival_rates, dtype=float)
    lam = float(arr_arr.mean())
    ca2 = float((arr_arr.std(ddof=0) ** 2) / (lam ** 2)) if lam > 0 else 1.0

    if service_durations_hr:
        srv_arr = np.asarray(service_durations_hr, dtype=float)
        mean_srv = float(srv_arr.mean())
        mu = 1.0 / mean_srv if mean_srv > 0 else 1.0
        cs2 = float((srv_arr.std(ddof=0) ** 2) / (mean_srv ** 2)) if mean_srv > 0 else 1.0
    else:
        mu = 1.5  # Nominal 40 min mean session
        cs2 = 0.8

    c = max(1, num_connectors)
    rho = lam / (c * mu) if mu > 0 else 0.0

    return {
        "lambda_per_hr": round(lam, 4),
        "mu_per_hr": round(mu, 4),
        "rho": round(rho, 4),
        "ca2": round(ca2, 4),
        "cs2": round(cs2, 4),
    }

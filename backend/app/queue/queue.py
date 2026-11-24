"""Queue waiting time estimation module for CERCOS.

Implements pure analytical queue models:
1. Erlang-C formula for M/M/c multi-server queues.
2. Allen-Cunneen approximation for M/G/c queues with general service time distributions.

Pure functions with zero database or HTTP I/O.
"""
import math


def erlang_c(c: int, a: float) -> float:
    """Calculate the probability of waiting in an M/M/c queue (Erlang-C formula).

    Parameters
    ----------
    c : int
        Number of parallel servers (active charging connectors). Must be >= 1.
    a : float
        Offered traffic load (arrival_rate / service_rate = lambda / mu).

    Returns
    -------
    float
        Probability of waiting P(W > 0), bounded in [0.0, 1.0].
        If offered load a >= c, the queue is saturated / unstable and returns 1.0.

    Formula
    -------
        P(wait) = t / (s + t)
        where:
            s = sum_{k=0}^{c-1} (a^k / k!)
            t = (a^c / c!) * (1 / (1 - a / c))
    """
    if c < 1:
        raise ValueError("Number of servers c must be >= 1")
    if a < 0:
        raise ValueError("Offered load a must be non-negative")
    if a == 0:
        return 0.0
    if a >= c:
        return 1.0

    s = sum(a**k / math.factorial(k) for k in range(c))
    t = (a**c / math.factorial(c)) * (1.0 / (1.0 - a / c))
    return float(t / (s + t))


def mmc_wq(lam: float, mu: float, c: int) -> float:
    """Calculate the mean waiting time in queue for an M/M/c queue.

    Parameters
    ----------
    lam : float
        Mean arrival rate (arrivals per time unit, e.g., vehicles/hour).
    mu : float
        Mean service rate per server (sessions per time unit, e.g., charges/hour).
    c : int
        Number of identical parallel servers (connectors).

    Returns
    -------
    float
        Expected queue waiting time Wq in hours (same unit as 1/mu).
        Returns float("inf") if the queue is saturated (lambda >= c * mu).

    Formula
    -------
        Wq = P(wait) / (c * mu - lambda)
    """
    if lam < 0 or mu <= 0:
        raise ValueError("Arrival rate must be >= 0 and service rate must be > 0")
    if lam == 0:
        return 0.0

    a = lam / mu
    if a >= c:
        return float("inf")

    p_wait = erlang_c(c, a)
    denominator = c * mu - lam
    if denominator <= 0:
        return float("inf")
    return float(p_wait / denominator)


def allen_cunneen_mgc_wq(
    lam: float,
    mu: float,
    c: int,
    ca2: float = 1.0,
    cs2: float = 1.0,
) -> float:
    """Calculate the mean waiting time for an M/G/c queue using Allen-Cunneen approximation.

    Parameters
    ----------
    lam : float
        Mean arrival rate (arrivals per time unit).
    mu : float
        Mean service rate per server (services per time unit).
    c : int
        Number of parallel servers.
    ca2 : float, default=1.0
        Squared coefficient of variation of inter-arrival times (Var(A) / E[A]^2).
        For Poisson arrivals (exponential inter-arrival), ca2 = 1.0.
    cs2 : float, default=1.0
        Squared coefficient of variation of service times (Var(S) / E[S]^2).
        For exponential service, cs2 = 1.0.
        Field EV charging typically exhibits cs2 in [0.35, 1.5].

    Returns
    -------
    float
        Expected waiting time in queue Wq (hours).
        Returns float("inf") if saturated.
        When ca2 == 1.0 and cs2 == 1.0, returns the exact M/M/c value.

    Formula
    -------
        Wq(M/G/c) approx Wq(M/M/c) * ((ca2 + cs2) / 2)
    """
    if ca2 < 0 or cs2 < 0:
        raise ValueError("Squared coefficients of variation ca2 and cs2 must be non-negative")

    base_wq = mmc_wq(lam, mu, c)
    if math.isinf(base_wq) or base_wq == 0.0:
        return base_wq

    scv_factor = (ca2 + cs2) / 2.0
    return float(base_wq * scv_factor)


def estimate_station_wait_min(
    station_power_kw: float,
    num_connectors: int,
    arrival_rate_per_hour: float,
    avg_battery_kwh: float = 40.0,
    avg_soc_topup: float = 0.35,
    ca2: float = 1.0,
    cs2: float = 1.0,
    cap_min: float = 120.0,
) -> float:
    """Convenience estimator returning wait time in minutes for station candidate evaluation.

    Parameters
    ----------
    station_power_kw : float
        Station effective power capacity in kW.
    num_connectors : int
        Number of connectors of matching type.
    arrival_rate_per_hour : float
        Estimated arrival rate in vehicles/hour.
    avg_battery_kwh : float
        Average vehicle battery capacity in kWh (default 40.0 kWh).
    avg_soc_topup : float
        Average energy top-up fraction (default 35% SoC delta).
    ca2 : float
        Arrival SCV (default 1.0).
    cs2 : float
        Service SCV (default 1.0).
    cap_min : float
        Upper cap for estimated wait in minutes to prevent infinite scores.

    Returns
    -------
    float
        Estimated queue wait in minutes, capped at cap_min.
    """
    if num_connectors < 1 or station_power_kw <= 0:
        return cap_min

    # Average energy delivered per charge session: (avg_soc_topup * avg_battery_kwh)
    # Average service time in hours: energy_kwh / station_power_kw
    mean_charge_kwh = max(1.0, avg_soc_topup * avg_battery_kwh)
    mean_service_time_h = mean_charge_kwh / station_power_kw
    mu = 1.0 / max(mean_service_time_h, 0.05)  # Service rate per connector

    wq_hours = allen_cunneen_mgc_wq(
        lam=arrival_rate_per_hour,
        mu=mu,
        c=num_connectors,
        ca2=ca2,
        cs2=cs2,
    )

    if math.isinf(wq_hours):
        return cap_min

    wq_min = wq_hours * 60.0
    return float(min(wq_min, cap_min))

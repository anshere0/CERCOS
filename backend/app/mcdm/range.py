"""EV range, battery consumption, and reachability model for CERCOS.

Enforces the non-negotiable 8.0% safety reserve constraint:
    usable_energy = max(0.0, (soc_pct - 8.0) / 100.0 * battery_kwh)
and provides multi-factor energy consumption modeling.
"""


def usable_energy_kwh(
    battery_kwh: float,
    current_soc_pct: float,
    reserve_soc_pct: float = 8.0,
) -> float:
    """Calculate the usable battery energy strictly above the safety reserve.

    Parameters
    ----------
    battery_kwh : float
        Nominal battery capacity in kWh.
    current_soc_pct : float
        Current battery State of Charge in percent [0.0, 100.0].
    reserve_soc_pct : float, default=8.0
        Mandatory safety reserve percentage (default 8.0%).

    Returns
    -------
    float
        Usable energy in kWh available for driving before hitting reserve.
    """
    if battery_kwh <= 0:
        raise ValueError("Battery capacity must be > 0 kWh")
    usable_soc = max(0.0, current_soc_pct - reserve_soc_pct)
    return float((usable_soc / 100.0) * battery_kwh)


def effective_wh_per_km(
    base_wh_per_km: float,
    speed_kmh: float = 45.0,
    load_factor: float = 1.0,
    ac_factor: float = 1.0,
    gradient_pct: float = 0.0,
) -> float:
    """Calculate adjusted energy consumption rate based on operating conditions.

    Parameters
    ----------
    base_wh_per_km : float
        Baseline manufacturer/standard rated energy consumption in Wh/km.
    speed_kmh : float, default=45.0
        Cruising/corridor speed in km/h. Aerodynamic drag increases consumption
        above nominal urban speed (45 km/h).
    load_factor : float, default=1.0
        Payload multiplier (e.g. 1.0 = driver only, 1.15 = full passengers/cargo).
    ac_factor : float, default=1.0
        Climate control multiplier (e.g. 1.0 = off, 1.10 = summer AC active).
    gradient_pct : float, default=0.0
        Road gradient in percent (e.g. +2% incline).

    Returns
    -------
    float
        Adjusted energy consumption rate in Wh/km.
    """
    if base_wh_per_km <= 0:
        raise ValueError("Base Wh/km must be positive")

    # Speed drag penalty above nominal 45 km/h: quadratic aerodynamic component
    speed_penalty = 1.0
    if speed_kmh > 45.0:
        # Approximate drag overhead (+15% at 80 km/h, +30% at 100 km/h)
        speed_penalty = 1.0 + 0.0003 * ((speed_kmh - 45.0) ** 1.8)

    # Elevation grade penalty (+5% per 1% incline)
    gradient_multiplier = max(0.5, 1.0 + (gradient_pct * 0.05))

    adjusted_wh = base_wh_per_km * speed_penalty * max(0.5, load_factor) * max(0.5, ac_factor) * gradient_multiplier
    return float(round(adjusted_wh, 2))


def reachable_distance_km(
    battery_kwh: float,
    current_soc_pct: float,
    wh_per_km: float,
    reserve_soc_pct: float = 8.0,
) -> float:
    """Calculate maximum reachable distance keeping the safety reserve intact.

    Parameters
    ----------
    battery_kwh : float
        Battery capacity in kWh.
    current_soc_pct : float
        Current battery SoC in percent.
    wh_per_km : float
        Energy consumption rate in Wh/km.
    reserve_soc_pct : float, default=8.0
        Mandatory safety reserve percentage.

    Returns
    -------
    float
        Maximum reachable distance in kilometers, rounded to 1 decimal place.
    """
    if wh_per_km <= 0:
        raise ValueError("wh_per_km must be > 0")

    usable_kwh = usable_energy_kwh(battery_kwh, current_soc_pct, reserve_soc_pct)
    dist_km = (usable_kwh * 1000.0) / wh_per_km
    return float(round(dist_km, 1))


def arrival_soc_pct(
    current_soc_pct: float,
    distance_km: float,
    battery_kwh: float,
    wh_per_km: float,
) -> float:
    """Calculate predicted battery State of Charge upon arriving at a station.

    Parameters
    ----------
    current_soc_pct : float
        Starting SoC in percent.
    distance_km : float
        Total driving distance from origin to the candidate station in km.
    battery_kwh : float
        Battery capacity in kWh.
    wh_per_km : float
        Energy consumption rate in Wh/km.

    Returns
    -------
    float
        Arrival SoC in percent [can be negative if vehicle runs out of charge].
    """
    if battery_kwh <= 0:
        raise ValueError("Battery capacity must be > 0 kWh")

    kwh_consumed = (distance_km * wh_per_km) / 1000.0
    soc_drop = (kwh_consumed / battery_kwh) * 100.0
    arr_soc = current_soc_pct - soc_drop
    return float(round(arr_soc, 2))


def charge_requirements(
    arrival_soc: float,
    target_soc: float,
    battery_kwh: float,
    effective_kw: float,
) -> tuple[float, float]:
    """Calculate energy to deliver and required charging duration in minutes.

    Parameters
    ----------
    arrival_soc : float
        SoC on arrival in percent.
    target_soc : float
        Desired target SoC in percent (typically 80.0% to avoid CC-CV taper).
    battery_kwh : float
        Battery capacity in kWh.
    effective_kw : float
        Effective charging power P_eff = min(P_station, P_vehicle) in kW.

    Returns
    -------
    tuple[float, float]
        (kwh_to_charge, charge_duration_min)
    """
    if target_soc <= arrival_soc:
        return 0.0, 0.0
    if effective_kw <= 0:
        raise ValueError("Effective charging power must be positive")

    kwh_needed = ((target_soc - max(0.0, arrival_soc)) / 100.0) * battery_kwh
    duration_hours = kwh_needed / effective_kw
    duration_min = duration_hours * 60.0
    return float(round(kwh_needed, 2)), float(round(duration_min, 1))

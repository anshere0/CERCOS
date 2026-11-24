"""Decision modes, criteria bounds, and weight vector management for CERCOS.

Loads:
- `config/criteria_bounds.yaml` -> Anchored normalization bounds.
- `config/weights.yaml` -> Mode weights with segment-specific overrides (AHP/BWM).
"""
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from app.mcdm.criteria import CRITERIA_NAMES

# Default criteria bounds fallback matching config/criteria_bounds.yaml
DEFAULT_BOUNDS: dict[str, list[float]] = {
    "detour_km": [0.0, 10.0],
    "cost_inr_per_kwh": [8.0, 28.0],
    "wait_min": [0.0, 60.0],
    "effective_kw": [3.3, 60.0],
    "rating": [1.0, 5.0],
    "arrival_soc_pct": [0.0, 100.0],
}

# Default weights fallback matching config/weights.yaml
DEFAULT_MODE_WEIGHTS: dict[str, list[float]] = {
    "Cheapest": [0.10, 0.50, 0.10, 0.10, 0.05, 0.15],
    "Fastest": [0.10, 0.05, 0.25, 0.45, 0.05, 0.10],
    "Shortest": [0.45, 0.05, 0.25, 0.10, 0.05, 0.10],
    "HighestRated": [0.10, 0.10, 0.10, 0.10, 0.50, 0.10],
    "BatterySafe": [0.10, 0.05, 0.05, 0.10, 0.05, 0.65],
    "Balanced": [0.20, 0.20, 0.20, 0.15, 0.10, 0.15],
}


def find_config_file(filename: str) -> Path | None:
    """Locate a configuration file across project directory roots."""
    candidates = [
        Path(f"config/{filename}"),
        Path(f"../config/{filename}"),
        Path(f"../../config/{filename}"),
        Path(__file__).resolve().parents[3] / "config" / filename,
    ]
    for p in candidates:
        if p.exists() and p.is_file():
            return p
    return None


def load_criteria_bounds(path: Path | str | None = None) -> np.ndarray:
    """Load anchored normalization bounds from YAML as a (6, 2) numpy array.

    Parameters
    ----------
    path : Path | str | None
        Path to criteria_bounds.yaml. If None, auto-discovers in project roots.

    Returns
    -------
    np.ndarray
        Array of shape (6, 2) corresponding to CRITERIA_NAMES ordering.
    """
    data = DEFAULT_BOUNDS
    if path:
        p = Path(path)
        if p.exists():
            data = yaml.safe_load(p.read_text(encoding="utf-8"))
    else:
        cfg = find_config_file("criteria_bounds.yaml")
        if cfg:
            data = yaml.safe_load(cfg.read_text(encoding="utf-8"))

    bounds_list: list[list[float]] = []
    for crit in CRITERIA_NAMES:
        b = data.get(crit, DEFAULT_BOUNDS.get(crit, [0.0, 1.0]))
        bounds_list.append([float(b[0]), float(b[1])])

    return np.array(bounds_list, dtype=float)


def load_all_mode_weights(
    path: Path | str | None = None,
    segment: str | None = None,
) -> dict[str, np.ndarray]:
    """Load criteria weights for all 6 modes, applying segment override if present.

    Parameters
    ----------
    path : Path | str | None
        Path to weights.yaml.
    segment : str | None
        Vehicle segment (E2W, E3W, E4W, ELCV).

    Returns
    -------
    dict[str, np.ndarray]
        Dictionary mapping mode name to 6-element weight vector.
    """
    raw_data: dict[str, Any] = {}
    if path:
        p = Path(path)
        if p.exists():
            raw_data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    else:
        cfg = find_config_file("weights.yaml")
        if cfg:
            raw_data = yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}

    defaults = raw_data.get("default", DEFAULT_MODE_WEIGHTS)
    overrides = raw_data.get("segment_overrides", {})
    seg_override = overrides.get(segment, {}) if segment else {}

    result: dict[str, np.ndarray] = {}
    for mode, w_list in defaults.items():
        # Check if segment provides an override for this mode
        final_w = seg_override.get(mode, w_list)
        arr = np.asarray(final_w, dtype=float)
        # Verify normalization (weights must sum to 1.0)
        s = arr.sum()
        if s > 0:
            arr = arr / s
        result[mode] = arr

    return result


def get_weights_for_mode(
    mode: str,
    segment: str | None = None,
    path: Path | str | None = None,
) -> np.ndarray:
    """Retrieve verified criteria weight vector for a specific mode and segment.

    Parameters
    ----------
    mode : str
        Decision mode ("Cheapest", "Fastest", "Shortest", "HighestRated", "BatterySafe", "Balanced").
    segment : str | None
        Vehicle segment ("E2W", "E3W", "E4W", "ELCV").
    path : Path | str | None
        Optional config path.

    Returns
    -------
    np.ndarray
        Weight vector of length 6 summing to 1.0.
    """
    all_weights = load_all_mode_weights(path=path, segment=segment)
    if mode in all_weights:
        return all_weights[mode]
    return all_weights.get("Balanced", np.array(DEFAULT_MODE_WEIGHTS["Balanced"], dtype=float))

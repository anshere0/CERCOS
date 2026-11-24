"""Driver decision modes and criteria weights endpoint."""
from pathlib import Path
from typing import Any

import yaml
from fastapi import APIRouter

router = APIRouter()


def load_weights_config() -> dict[str, Any]:
    """Load criteria weights configuration from config/weights.yaml."""
    possible_paths = [
        Path("config/weights.yaml"),
        Path("../config/weights.yaml"),
        Path(__file__).resolve().parents[5] / "config" / "weights.yaml",
    ]
    for p in possible_paths:
        if p.exists():
            return yaml.safe_load(p.read_text(encoding="utf-8"))
    raise FileNotFoundError("config/weights.yaml could not be found")


MODE_DESCRIPTIONS = {
    "Cheapest": "Prioritizes charging tariff and minimizes total trip charging cost (w_cost = 0.50).",
    "Fastest": "Maximizes effective charging power and minimizes waiting time (w_power = 0.45, w_wait = 0.25).",
    "Shortest": "Minimizes highway detour distance to the nearest station (w_detour = 0.45).",
    "HighestRated": "Prioritizes highly rated facilities with reliable amenities (w_rating = 0.50).",
    "BatterySafe": "Maximizes arrival State of Charge and buffers against range anxiety (w_soc = 0.65).",
    "Balanced": "Harmonized trade-off across cost, detour, power, waiting, and battery reserve.",
}


@router.get("/modes")
def get_decision_modes() -> dict[str, Any]:
    """List 6 standardized driver decision modes, criteria names, and default BWM weight vectors."""
    cfg = load_weights_config()
    criteria: list[str] = cfg.get("criteria", [])
    default_weights: dict[str, list[float]] = cfg.get("default", {})

    return {
        "criteria": criteria,
        "modes": default_weights,
        "descriptions": MODE_DESCRIPTIONS,
    }

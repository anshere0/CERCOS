"""Vehicle catalog and technical charging limits endpoint."""
from pathlib import Path
from typing import Any, Literal

import yaml
from fastapi import APIRouter, Query

from app.schemas.vehicle import VehicleRead

router = APIRouter()


def load_vehicles_config() -> list[dict[str, Any]]:
    """Load vehicle profiles from config/vehicles.yaml."""
    possible_paths = [
        Path("config/vehicles.yaml"),
        Path("../config/vehicles.yaml"),
        Path(__file__).resolve().parents[5] / "config" / "vehicles.yaml",
    ]
    for p in possible_paths:
        if p.exists():
            data = yaml.safe_load(p.read_text(encoding="utf-8"))
            return data.get("vehicles", [])
    raise FileNotFoundError("config/vehicles.yaml could not be found")


@router.get("/vehicles", response_model=list[VehicleRead])
def get_vehicles(
    segment: Literal["E2W", "E3W", "E4W", "ELCV"] | None = Query(
        None, description="Filter vehicles by fleet segment (E2W, E3W, E4W, ELCV)"
    ),
) -> list[dict[str, Any]]:
    """List vehicle catalog intake parameters and technical charging envelopes."""
    raw_vehicles = load_vehicles_config()
    vehicles: list[dict[str, Any]] = []

    for idx, v in enumerate(raw_vehicles, start=1):
        veh_dict = {
            "vehicle_id": idx,
            "model_name": v.get("model_name"),
            "segment": v.get("segment"),
            "battery_kwh": v.get("battery_kwh"),
            "wh_per_km": v.get("wh_per_km"),
            "max_dc_kw": v.get("max_dc_kw"),
            "max_ac_kw": v.get("max_ac_kw"),
            "connector_types": v.get("connector_types", []),
            "source": v.get("source", "catalog"),
            "confidence": float(v.get("confidence", 0.90)),
        }
        if segment is None or veh_dict["segment"] == segment:
            vehicles.append(veh_dict)

    return vehicles

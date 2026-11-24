"""CERCOS API v1 master router mounting all operational and diagnostic endpoints."""
import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter

from app.api.v1.endpoints.field import router as field_router
from app.api.v1.endpoints.modes import router as modes_router
from app.api.v1.endpoints.recommend import router as recommend_router
from app.api.v1.endpoints.stations import router as stations_router
from app.api.v1.endpoints.vehicles import router as vehicles_router
from app.core.db import check_database_status, fetch_stations_from_db

router = APIRouter()
api_v1_router = router  # export alias

router.include_router(modes_router, tags=["Modes"])
router.include_router(vehicles_router, tags=["Vehicles"])
router.include_router(stations_router, tags=["Stations"])
router.include_router(field_router, tags=["Field Research"])
router.include_router(recommend_router, tags=["Recommendation Engine"])


@router.get("/status", tags=["System"])
def system_status() -> dict[str, Any]:
    """Report live database engine backend, real data provenance distribution, and policy targets."""
    db_info = check_database_status()
    stations = fetch_stations_from_db()
    by_source: dict[str, int] = {}
    for st in stations:
        src = st.get("source", "unknown")
        by_source[src] = by_source.get(src, 0) + 1

    policy_file = Path(__file__).resolve().parents[4] / "data" / "policy" / "mp_policy_benchmarks.json"
    policy_summary = json.loads(policy_file.read_text(encoding="utf-8")) if policy_file.exists() else {}

    return {
        "service": "CERCOS Backend API",
        "phase": "Phase-I (40% Scope)",
        "database": db_info,
        "stations_total": len(stations),
        "stations_by_source": by_source,
        "policy_benchmarks": policy_summary,
    }

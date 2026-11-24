"""CERCOS API v1 master router mounting all operational endpoints."""
from fastapi import APIRouter

from app.api.v1.endpoints.field import router as field_router
from app.api.v1.endpoints.modes import router as modes_router
from app.api.v1.endpoints.recommend import router as recommend_router
from app.api.v1.endpoints.stations import router as stations_router
from app.api.v1.endpoints.vehicles import router as vehicles_router

router = APIRouter()
api_v1_router = router  # export alias

router.include_router(modes_router, tags=["Modes"])
router.include_router(vehicles_router, tags=["Vehicles"])
router.include_router(stations_router, tags=["Stations"])
router.include_router(field_router, tags=["Field Research"])
router.include_router(recommend_router, tags=["Recommendation Engine"])

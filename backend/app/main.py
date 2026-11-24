"""FastAPI application entry point for CERCOS."""
from fastapi import FastAPI

from app.api.v1.router import router as api_v1_router

app = FastAPI(
    title="CERCOS API",
    description="Cognitive EV Route & Charging Optimization System API",
    version="0.1.0",
)

# Mount API v1 router
app.include_router(api_v1_router, prefix="/v1")


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}

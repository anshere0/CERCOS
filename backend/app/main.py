"""FastAPI application entry point for CERCOS."""
from fastapi import FastAPI

app = FastAPI(
    title="CERCOS API",
    description="Cognitive EV Route & Charging Optimization System API",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}

"""FastAPI application entry point.

This module defines the main FastAPI application and all HTTP endpoints.
"""

from typing import Any

from fastapi import FastAPI, Query

from .scheduler import start_scheduler
from .services import fetch_data, logger

app: FastAPI = FastAPI(title="Weather API", description="Test task for InfoTeCS")

scheduler = start_scheduler()


@app.on_event("shutdown")
def shutdown_scheduler() -> None:
    """Shutdown background scheduler on app exit."""
    scheduler.shutdown()
    logger.info("--- Scheduler shut down")


@app.get("/weather/current")
async def get_current_weather(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
) -> dict[str, Any]:
    """Return current temperature, wind speed, and pressure for coordinates."""
    data = await fetch_data(lat, lon)
    return data

"""FastAPI application entry point.

This module defines the main FastAPI application and all HTTP endpoints.
"""

from typing import Any

from fastapi import Depends, FastAPI

from .models import WeatherCurrentParams
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
    coords: WeatherCurrentParams = Depends(),
) -> dict[str, Any]:
    """Return current temperature, wind speed, and pressure for coordinates."""
    data = await fetch_data(coords.lat, coords.lon)
    return data

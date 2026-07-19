"""FastAPI application entry point.

This module defines the main FastAPI application and all HTTP endpoints.
"""

from typing import Any

from fastapi import Depends, FastAPI

from . import config, models
from .scheduler import start_scheduler
from .services import fetch_data, logger, split_fields_by_comma

app: FastAPI = FastAPI(title="Weather API", description="Test task for InfoTeCS")

scheduler = start_scheduler()


@app.on_event("shutdown")
def shutdown_scheduler() -> None:
    """Shutdown background scheduler on app exit."""
    scheduler.shutdown()
    logger.info("--- Scheduler shut down")


@app.get("/weather/current")
async def get_current_weather(
    query: models.WeatherCurrentParams = Depends(),
) -> dict[str, Any]:
    """Return current temperature, wind speed, and pressure for coordinates."""
    fields = (
        split_fields_by_comma(query.fields) if query.fields else config.DEFAULT_PARAMS
    )
    data = await fetch_data(query.lat, query.lon, fields)
    return data

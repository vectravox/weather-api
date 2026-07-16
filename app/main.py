"""FastAPI application entry point.

This module defines the main FastAPI application and all HTTP endpoints.
"""

from fastapi import FastAPI, Query
from .services import fetch_current_weather

app: FastAPI = FastAPI(title="Weather API", description="Test task for InfoTeCS")


@app.get("/weather/current")
async def get_current_weather(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
) -> dict[str, float]:
    """Method №1: get params temperature, wind speed, pressure."""

    data = await fetch_current_weather(lat, lon)
    return data

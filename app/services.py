"""Service layer for weather API.

This module contains business logic for:
- Parsing and validating query parameters
- Fetching weather data from Open-Meteo API
"""

from datetime import UTC, datetime
from logging import getLogger
from typing import Any, Literal

import aiohttp
from fastapi import HTTPException

from . import config

ForecastType = Literal["current", "hourly"]

logger = getLogger("uvicorn")


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(UTC)


def split_fields_by_comma(fields: str) -> list[str]:
    """Split query parameter with commas into separate items."""
    return [f.strip() for f in fields.split(",") if f.strip()]


async def fetch_data(
    lat: float,
    lon: float,
    fetch_params: list[str],
    forecast_type: ForecastType = "current",
) -> dict[str, Any]:
    """Fetch weather data from Open-Meteo API.

    Retrieves either current weather or hourly forecast for the specified
    location and parameters.

    Args:
        lat: Latitude in degrees (-90 to 90).
        lon: Longitude in degrees (-180 to 180).
        fetch_params: Parameter names to fetch separated by comma.
        forecast_type: Type of forecast to fetch.
            - "current": Real-time weather at the moment of request.
            - "hourly": Hourly forecast for the current day (24 entries).

    """
    try:
        async with aiohttp.ClientSession() as session:
            aiohttp_params: dict[str, float | int | list[str]] = {
                "latitude": lat,
                "longitude": lon,
                "forecast_days": 1,
            }
            aiohttp_params[forecast_type] = [config.OPEN_METEO_PARAMS[param] for param in fetch_params]

            async with session.get(
                config.OPEN_METEO_URL,
                params=aiohttp_params,
                timeout=aiohttp.ClientTimeout(total=config.CLIENT_TIMEOUT_SECONDS),
            ) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=502,
                        detail=f"Open-Meteo API error: status {response.status}",
                    )
                response_json: dict[str, Any] = await response.json()
                data: dict[str, Any] = response_json[forecast_type]
                return {param: data[config.OPEN_METEO_PARAMS[param]] for param in fetch_params}

    except aiohttp.ClientError as err:
        raise HTTPException(
            status_code=502, detail="Open-Meteo API connection error"
        ) from err

    except KeyError as err:
        raise HTTPException(status_code=502, detail=f"Invalid query parameter: {err}") from err

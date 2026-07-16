"""Service layer for weather API.

This module contains business logic for:
- Parsing and validating query parameters
- Fetching weather data from Open-Meteo API
"""

import aiohttp
from typing import Any
from fastapi import HTTPException
from . import config
from typing import Literal


ForecastType = Literal["current", "hourly"]


def split_params_by_comma(params: list[str]) -> list[str]:
    """Splits query parameters with comma into separate items.

    Example:
        # For query strings like:
        /weather/current?lat=56.36&lon=84.51&params=temp,wind_speed&params=pressure

        >>> split_params_by_comma(["temp,wind_speed", "pressure"])
        ["temp", "wind_speed", "pressure"]
    """

    result: list[str] = []

    for param in params:
        if "," in param:
            result.extend([f.strip() for f in param.split(",") if f.strip()])
        elif param.strip():
            result.append(param.strip())

    return result


def parse_params(params: list[str] | None) -> list[str]:
    """Parse query parameters and apply defaults."""

    if params is None:
        return config.DEFAULT_PARAMS.copy()

    result = split_params_by_comma(params)

    if not result:
        return config.DEFAULT_PARAMS.copy()

    return result


async def fetch_data(
    lat: float,
    lon: float,
    fetch_params: list[str] | None = None,
    forecast_type: ForecastType = "current",
) -> dict[str, Any]:
    """Fetch current weather data from Open-Meteo API.

    Example:
        >>> await fetch_current_weather(55.7558, 37.6173)
        {"temp": 18.5, "wind_speed": 3.2, "pressure": 1012.0}
    """

    fetch_params = parse_params(fetch_params)

    try:
        async with aiohttp.ClientSession() as session:
            params: dict[str, float | int | list[str]] = {
                "latitude": lat,
                "longitude": lon,
                "forecast_days": 1,
            }
            params[forecast_type] = [
                config.OPEN_METEO_PARAMS[param] for param in fetch_params
            ]

            async with session.get(
                config.OPEN_METEO_URL,
                params=params,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=502,
                        detail=f"Open-Meteo API error: status {response.status}",
                    )

                response_json: dict[str, Any] = await response.json()
                data: dict[str, Any] = response_json[forecast_type]

                return {
                    param: data[config.OPEN_METEO_PARAMS[param]]
                    for param in fetch_params
                }

    except aiohttp.ClientError as err:
        raise HTTPException(
            status_code=502, detail="Open-Meteo API connection error"
        ) from err

    except KeyError as err:
        raise HTTPException(status_code=502, detail="Invalid query parameter") from err

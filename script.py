import aiohttp
from fastapi import FastAPI, HTTPException, Query
from typing import Any

OPEN_METEO_URL: str = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_PARAMS: dict[str, str] = {
    "temp": "temperature_2m",
    "wind_speed": "wind_speed_10m",
    "pressure": "surface_pressure",
    "humidity": "relative_humidity_2m",
    "precipitation": "precipitation",
}
DEFAULT_PARAMS: list[str] = ["temp", "wind_speed", "pressure"]


app: FastAPI = FastAPI(title="Weather API", description="Test task for InfoTeCS")


def split_params_by_comma(params: list[str]) -> list[str]:
    """Splits query parameters with comma into separate items.

    Example:
        # /weather/current?lat=56.36&lon=84.51&params=temp,wind_speed&params=pressure
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
        return DEFAULT_PARAMS.copy()

    result = split_params_by_comma(params)

    if not result:
        return DEFAULT_PARAMS.copy()

    return result


@app.get("/weather/current")
async def get_current_weather(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
) -> dict[str, float]:
    """Method №1: get params temperature, wind speed, pressure."""

    data = await fetch_current_weather(lat, lon)
    return data


async def fetch_current_weather(
    lat: float,
    lon: float,
    fetch_params: list[str] | None = None,
) -> dict[str, float]:
    """Fetch current weather data from Open-Meteo API.

    Example:
        >>> await fetch_current_weather(55.7558, 37.6173)
        {"temp": 18.5, "wind_speed": 3.2, "pressure": 1012.0}
    """

    fetch_params = parse_params(fetch_params)

    try:
        async with aiohttp.ClientSession() as session:
            params: dict[str, float | list[str]] = {
                "latitude": lat,
                "longitude": lon,
                "current": [OPEN_METEO_PARAMS[param] for param in fetch_params],
            }

            async with session.get(
                OPEN_METEO_URL,
                params=params,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=502,
                        detail=f"Open-Meteo API error: status {response.status}",
                    )

                response_json: dict[str, Any] = await response.json()
                weather_data: dict[str, Any] = response_json["current"]

                return {
                    param: float(weather_data[OPEN_METEO_PARAMS[param]])
                    for param in fetch_params
                }

    except aiohttp.ClientError:
        raise HTTPException(status_code=502, detail="Open-Meteo API connection error")

    except KeyError:
        raise HTTPException(status_code=502, detail="Invalid query parameter")

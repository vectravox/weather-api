import aiohttp
from fastapi import FastAPI, HTTPException, Query
from typing import Any

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_PARAMETERS: dict[str, str] = {
    "temp": "temperature_2m",
    "wind_speed": "wind_speed_10m",
    "pressure": "surface_pressure",
    "humidity": "relative_humidity_2m",
    "precipitation": "precipitation",
}


app: FastAPI = FastAPI(title="Weather API", description="Test task for InfoTeCS")


@app.get("/weather/current")
async def get_current_weather(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    current: list[str] = Query(None, description="Fields to return"),
) -> dict[str, float]:
    """Method №1: get current temperature, wind speed, pressure."""

    # Default params
    if current is None or current[0] == "":
        current = ["temp", "wind_speed", "pressure"]

    data = await fetch_current_weather(lat, lon, current)
    return data


async def fetch_current_weather(
    lat: float,
    lon: float,
    fetch_params: list[str],
) -> dict[str, float]:
    """Fetch current weather data from Open-Meteo API.

    Example:
        >>> await fetch_current_weather(55.7558, 37.6173)
        {"temp": 18.5, "wind_speed": 3.2, "pressure": 1012.0}
    """

    try:
        async with aiohttp.ClientSession() as session:
            params: dict[str, float | list[str]] = {
                "latitude": lat,
                "longitude": lon,
                "current": [
                    OPEN_METEO_PARAMETERS.get(param, param) for param in fetch_params
                ],
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
                    param: float(weather_data[OPEN_METEO_PARAMETERS.get(param, param)])
                    for param in fetch_params
                }

    except aiohttp.ClientError:
        raise HTTPException(status_code=502, detail="Open-Meteo API connection error")

    # except KeyError:
    #     raise HTTPException(status_code=502, detail="Invalid Key")

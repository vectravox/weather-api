import aiohttp
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import TypeAlias

JsonDict: TypeAlias = dict[str, "JsonDict | list | str | int | float | bool | None"]

app: FastAPI = FastAPI(title="Weather API", description="Test task for InfoTeCS")


# Pydantic Models
class CurrentWeatherResponse(BaseModel):
    temp: float = Field(description="Temperature in °C")
    wind_speed: float = Field(description="Wind speed in km/h")
    pressure: float = Field(description="Atmospheric pressure in gPa")


OPEN_METEO_PARAMETER_NAMES: dict[str, str] = {
    "temp": "temperature_2m",
    "wind_speed": "wind_speed_10m",
    "pressure": "surface_pressure",
    "humidity": "relative_humidity_2m",
    "precipitation": "precipitation",
}

# Reversed OPEN_METEO_PARAMETER_NAMES dict
SHORT_PARAMETER_NAMES: dict[str, str] = {v: k for k, v in OPEN_METEO_PARAMETER_NAMES.items()}


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello, InfoTeCS!"}


@app.get("/weather/current")
async def get_current_weather(
    lat: float = Query(..., ge=-90, le=90, description="latitude"),
    lon: float = Query(..., ge=-180, le=180, description="longitude"),
) -> CurrentWeatherResponse:
    """Method №1: current temperature, wind speed, pressure."""
    data = await fetch_current_weather(lat, lon)
    return CurrentWeatherResponse(**data)


async def fetch_current_weather(
    lat: float, lon: float, params: list[str] = ["temp", "wind_speed", "pressure"]
) -> JsonDict:
    """Current weather Open-Meteo API request."""
    url = "https://api.open-meteo.com/v1/forecast"

    requested_params = {
        "latitude": lat,
        "longitude": lon,
        "current": [OPEN_METEO_PARAMETER_NAMES[param] for param in params],
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, params=requested_params, timeout=10
            ) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=502,
                        detail=f"Open-Meteo API error: status {response.status}",
                    )
                response_json: JsonDict = await response.json()
                weather_data: JsonDict = response_json["current"]
                return {
                    SHORT_PARAMETER_NAMES[key]: float(weather_data[key])
                    for key in requested_params["current"]
                }

    except aiohttp.ClientError:
        raise HTTPException(status_code=502, detail="Open-Meteo API connection error")

    except KeyError:
        raise HTTPException(
            status_code=502, detail="Unexpected Open-Meteo API response"
        )

import aiohttp
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import TypeAlias

JsonDict: TypeAlias = dict[str, "JsonDict | list | str | int | float | bool | None"]
WeatherData: TypeAlias = dict[str, float]

app: FastAPI = FastAPI(title="Weather API", description="Test task for InfoTeCS")


# Pydantic Models
class CurrentWeatherResponse(BaseModel):
    temperature_2m: float = Field(description="Temperature in °C")
    wind_speed_10m: float = Field(description="Wind speed in km/h")
    surface_pressure: float = Field(description="Atmospheric pressure in gPa")


API_PARAMETER_NAMES: dict[str, str] = {
    "temp": "temperature_2m",
    "wind": "wind_speed_10m",
    "pressure": "surface_pressure",
    "humidity": "relative_humidity_2m",
    "precipitation": "precipitation",
}


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


async def fetch_current_weather(lat: float, lon: float) -> JsonDict:
    """Current weather Open-Meteo API request."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ["temperature_2m", "wind_speed_10m", "surface_pressure"],
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=502,
                        detail=f"Open-Meteo API error: status {response.status}",
                    )
                response_json = await response.json()
                weather_data: WeatherData = response_json["current"]
                return {
                    k: weather_data[k] for k in params["current"] if k in weather_data
                }

    except aiohttp.ClientError:
        raise HTTPException(status_code=502, detail="Open-Meteo API connection error")

    except KeyError:
        raise HTTPException(
            status_code=502, detail="Unexpected Open-Meteo API response"
        )

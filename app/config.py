"""Configuration constants for the Weather API."""

OPEN_METEO_URL: str = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_PARAMS: dict[str, str] = {
    "temp": "temperature_2m",
    "wind_speed": "wind_speed_10m",
    "pressure": "surface_pressure",
    "humidity": "relative_humidity_2m",
    "precipitation": "precipitation",
}
DEFAULT_PARAMS: list[str] = ["temp", "wind_speed", "pressure"]

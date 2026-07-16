"""Configuration constants for the Weather API."""

DATABASE_URL: str = "sqlite:///./weather.db"
JOBS_STATE_URL: str = "sqlite:///./jobs.db"
FORECAST_UPDATE_INTERVAL_MINUTES = 1 # Delay between forecast updates
REQUEST_DELAY_SECONDS = 0 # Delay between Open-Meteo requests for every city on forecast updates
OPEN_METEO_URL: str = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_PARAMS: dict[str, str] = {
    "temp": "temperature_2m",
    "wind_speed": "wind_speed_10m",
    "pressure": "surface_pressure",
    "humidity": "relative_humidity_2m",
    "precipitation": "precipitation",
}
DEFAULT_PARAMS: list[str] = ["temp", "wind_speed", "pressure"]

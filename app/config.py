"""Configuration constants for the Weather API."""

APP_DATABASE_URL: str = "sqlite:///./weather.db"
CLIENT_TIMEOUT_SECONDS = 10
DEFAULT_PARAMS: list[str] = ["temp", "wind_speed", "pressure"]
DELAY_BETWEEN_REQUESTS_SECONDS = 2 # Delay between requests to avoid Open-Meteo API rate limiting
FORECAST_UPDATE_INTERVAL_MINUTES = 15  # Delay between forecast updates
JOBS_DATABASE_URL: str = "sqlite:///./jobs.db"
OPEN_METEO_PARAMS: dict[str, str] = {
    "temp": "temperature_2m",
    "wind_speed": "wind_speed_10m",
    "pressure": "surface_pressure",
    "humidity": "relative_humidity_2m",
    "precipitation": "precipitation",
}
OPEN_METEO_URL: str = "https://api.open-meteo.com/v1/forecast"

# User validation
USERNAME_MIN_LENGTH: int = 3
USERNAME_MAX_LENGTH: int = 50
USERNAME_PATTERN: str = r"^[a-zA-Z0-9_]+$" # IMPORTANT: Update tests/test_users.py if you change this constraint

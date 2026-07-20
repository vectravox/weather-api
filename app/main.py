"""FastAPI application entry point.

This module defines the main FastAPI application and all HTTP endpoints.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Path, status
from sqlalchemy.orm import Session

from . import config, crud, models
from .database import get_db
from .scheduler import start_scheduler
from .services import fetch_data, logger, split_params_by_comma


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Manage application lifecycle: startup and shutdown events."""
    scheduler = start_scheduler()
    logger.info(
        f"--- Scheduler started. Forecasts will update every {config.FORECAST_UPDATE_INTERVAL_MINUTES} minutes."
    )
    yield
    scheduler.shutdown()
    logger.info("--- Scheduler shut down during application shutdown")


app: FastAPI = FastAPI(
    title="Weather API", description="Test task for InfoTeCS", lifespan=lifespan
)


@app.get("/weather/current")
async def get_current_weather(
    query: models.WeatherCurrentQuery = Depends(),
) -> dict[str, Any]:
    """Return current temperature, wind speed, and pressure for coordinates."""
    params = (
        split_params_by_comma(query.params) if query.params else config.DEFAULT_PARAMS
    )
    data = await fetch_data(query.lat, query.lon, params)
    return data


@app.post("/users", status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: models.UserRegister,
    db: Session = Depends(get_db),
) -> models.UserResponse:
    """Register a new user and return their ID."""
    user = crud.get_user_by_username(db, payload.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{payload.username}' already taken",
        )

    user = crud.create_user(db, payload.username)
    logger.info(f"--- New user registered: {user.username} (user_id: {user.id})")

    return models.UserResponse.model_validate(user)


@app.post("/users/{user_id}/cities", status_code=status.HTTP_201_CREATED)
async def add_city(
    payload: models.CityCreate = Depends(),
    db: Session = Depends(get_db),
) -> models.CityResponse:
    """Add a city to track weather forecasts for a specific user."""
    user = crud.get_user_by_id(db, payload.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {payload.user_id} not found",
        )

    city = crud.get_city_by_name_and_user(db, payload.name, payload.user_id)
    if city:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"City '{payload.name}' already tracked for this user",
        )

    city = crud.create_city(
        db,
        name=payload.name,
        lat=payload.lat,
        lon=payload.lon,
        user_id=payload.user_id,
    )

    try:
        forecast_data = await fetch_data(
            city.lat,
            city.lon,
            fetch_params=list(config.OPEN_METEO_PARAMS),
            forecast_type="hourly",
        )
        crud.update_city_forecast(db, city.id, forecast_data)

    except Exception as e:
        logger.error(f"--- Failed to fetch initial forecast for {city.name}: {e!r}")

    logger.info(
        f"--- City '{city.name}' added for user {user.username} (ID: {user.id})"
    )

    return models.CityResponse.model_validate(city)


@app.get("/users/{user_id}/cities")
def get_cities(
    query: models.CitiesQuery = Depends(),
    db: Session = Depends(get_db),
) -> list[models.CityResponse]:
    """Get all cities tracked by a specific user."""
    user = crud.get_user_by_id(db, query.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {query.user_id} not found",
        )

    cities = crud.get_cities_by_user(db, query.user_id)
    logger.info(
        f"--- Retrieved {len(cities)} cities for user {user.username} (ID: {query.user_id})"
    )

    return [models.CityResponse.model_validate(city) for city in cities]


@app.get("/users/{user_id}/cities/{city_name}/{hour}")
async def get_forecast_at_time(
    user_id: int = Path(..., gt=0, description="User ID must be more than 0"),
    city_name: str = Path(
        ..., min_length=1, max_length=100, pattern=r"^[a-zA-Z\s\-]+$"
    ),
    hour: int = Path(..., ge=0, le=23),
    query: models.ForecastQuery = Depends(),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Get weather forecast for a city at a specific time."""
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    city = crud.get_city_by_name_and_user(db, city_name, user_id)
    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"City '{city_name}' not found for this user",
        )

    if not city.forecast_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No forecast available for {city.name}",
        )

    params = (
        split_params_by_comma(query.params) if query.params else config.DEFAULT_PARAMS
    )

    forecast = {}

    for param in params:
        entry = city.forecast_data.get(param, None)
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No {param} data found for {city.name}",
            )
        forecast[param] = entry[hour]

    return forecast

"""FastAPI application entry point.

This module defines the main FastAPI application and all HTTP endpoints.
"""

from typing import Any

from fastapi import Depends, FastAPI, HTTPException, status

from . import config, crud, models
from .database import get_db
from .scheduler import start_scheduler
from .services import fetch_data, logger, split_params_by_comma

app: FastAPI = FastAPI(title="Weather API", description="Test task for InfoTeCS")

scheduler = start_scheduler()


@app.on_event("shutdown")
def shutdown_scheduler() -> None:
    """Shutdown background scheduler on app exit."""
    scheduler.shutdown()
    logger.info("--- Scheduler shut down")


@app.get("/weather/current")
async def get_current_weather(
    query: models.WeatherCurrentParams = Depends(),
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

    return user


@app.post("/users/{user_id}/cities", status_code=status.HTTP_201_CREATED)
async def add_city(
    payload: models.CityCreate,
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

    return city

"""FastAPI application entry point.

This module defines the main FastAPI application and all HTTP endpoints.
"""

from typing import Any

from fastapi import Depends, FastAPI, HTTPException, status

from . import config, models
from .crud import create_user, get_user_by_username
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


@app.post("/users/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: models.UserRegister,
    db: Session = Depends(get_db),
) -> models.UserResponse:
    """Register a new user and return their ID."""
    existing_user = get_user_by_username(db, payload.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{payload.username}' already taken"
        )

    user = create_user(db, payload.username)
    logger.info(f"--- New user registered: {user.username} (user_id: {user.id})")

    return user

"""Pydantic models for request and response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from . import config


class WeatherCurrentQuery(BaseModel):
    """Query parameters for weather endpoints."""

    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    params: str = Field(
        default="",
        description="Comma-separated list of weather parameters to return.",
    )


class UserRegister(BaseModel):
    """Model for user registration."""

    username: str = Field(
        ...,
        min_length=config.USERNAME_MIN_LENGTH,
        max_length=config.USERNAME_MAX_LENGTH,
        pattern=config.USERNAME_PATTERN,
        examples=["john_doe"],
    )


class UserResponse(BaseModel):
    """Response model for user data."""

    id: int
    username: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CityCreate(BaseModel):
    """Model for adding a new city to track."""

    name: str = Field(..., min_length=1, max_length=100)
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)


class CitiesQuery(BaseModel):
    """Query parameters for cities list of a user."""

    user_id: int = Field(..., gt=0)


class CityResponse(BaseModel):
    """Response model for city data."""

    id: int
    name: str
    lat: float
    lon: float
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ForecastQuery(BaseModel):
    """Query parameters for forecast at specific time."""

    params: str = Field(
        default="",
        description="Comma-separated: temp, humidity, wind_speed, precipitation, pressure",
    )

"""Pydantic models for request and response validation."""

from pydantic import BaseModel, Field
from datetime import datetime


class WeatherCurrentParams(BaseModel):
    """Query parameters for weather endpoints."""

    lat: float = Field(..., ge=-90, le=90, description="Latitude.")
    lon: float = Field(..., ge=-180, le=180, description="Longitude.")
    params: str = Field(
        default="",
        description="Comma-separated list of weather parameters to return.",
    )


class UserRegister(BaseModel):
    """Model for user registration."""

    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")


class UserResponse(BaseModel):
    """Response model for user data."""

    id: int
    username: str
    created_at: datetime

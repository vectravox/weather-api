"""Pydantic models for request and response validation."""

from pydantic import BaseModel, Field


class WeatherCurrentParams(BaseModel):
    """Query parameters for weather endpoints."""

    lat: float = Field(..., ge=-90, le=90, description="Latitude.")
    lon: float = Field(..., ge=-180, le=180, description="Longitude.")
    fields: str = Field(
        default = "",
        description="Comma-separated list of weather parameters to return.",
    )

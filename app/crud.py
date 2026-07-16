"""CRUD operations for database models.

This module provides functions for creating, reading, updating, and deleting
users, cities, and forecasts in the database.
"""

from typing import Any

from sqlalchemy.orm import Session

from .database import City, User
from .services import utc_now


def create_user(db: Session, username: str) -> User:
    """Create a new user."""
    user = User(username=username)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    """Get user by username."""
    return db.query(User).filter(User.username == username).first()


def create_city(
    db: Session,
    name: str,
    lat: float,
    lon: float,
    user_id: int,
) -> City:
    """Add a new city for a specific user."""
    city = City(name=name, latitude=lat, longitude=lon, user_id=user_id)
    db.add(city)
    db.commit()
    db.refresh(city)
    return city


def get_cities_by_user(db: Session, user_id: int) -> list[City]:
    """Get all cities for a specific user."""
    return db.query(City).filter(City.user_id == user_id).all()


def get_city_by_name_and_user(
    db: Session,
    name: str,
    user_id: int,
) -> City | None:
    """Get city by name for a specific user."""
    return db.query(City).filter(City.name == name, City.user_id == user_id).first()


def get_city_by_id(db: Session, city_id: int) -> City | None:
    """Get city by ID."""
    return db.query(City).filter(City.id == city_id).first()


def update_city_forecast(
    db: Session,
    city_id: int,
    forecast_data: dict[str, Any],
) -> City:
    """Update forecast for a city."""
    city = get_city_by_id(db, city_id)
    if not city:
        raise ValueError(f"City with id {city_id} not found")

    city.forecast_data = forecast_data # type: ignore
    city.forecast_updated_at = utc_now()
    db.commit()
    db.refresh(city)
    return city


def delete_city(db: Session, city_id: int) -> None:
    """Delete a city by ID."""
    city = get_city_by_id(db, city_id)
    if city:
        db.delete(city)
        db.commit()

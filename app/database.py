"""Database models and connection setup.

This module defines SQLAlchemy models for:
- Users (for multi-user support)
- Cities (with JSON forecast data)

All times are stored in UTC.
"""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker

# --- Database connection ---

DATABASE_URL: str = "sqlite:///./weather.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(UTC)


# --- Models ---


class User(Base):
    """User model for multi-user support."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    cities = relationship("City", back_populates="user", cascade="all, delete-orphan")


class City(Base):
    """City model with forecast data stored as JSON."""

    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=utc_now)

    # Forecast data — stored as JSON, updated every 15 minutes
    forecast_data = Column(JSON, nullable=True)  # list of hourly forecasts
    forecast_updated_at = Column(DateTime, nullable=True)

    # One city per user (case-insensitive check in code)
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_user_city"),)

    # Relationships
    user = relationship("User", back_populates="cities")

    def get_forecast_at_time(self, target_time: datetime) -> dict[str, Any] | None:
        """Get the closest forecast to the target time.

        Args:
            target_time: Time to find forecast for.

        Returns:
            Dictionary with forecast data, or None if no forecast available.

        """
        if not self.forecast_data:
            return None

        target_hour = target_time.hour
        closest = min(
            self.forecast_data,
            key=lambda f: abs(datetime.fromisoformat(f["time"]).hour - target_hour),
        )
        return closest


# --- Create tables ---

Base.metadata.create_all(bind=engine)


# --- Database dependency ---


def get_db() -> Session:
    """FastAPI dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

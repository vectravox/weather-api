"""Database models and connection setup."""

from collections.abc import Iterator
from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    String,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    sessionmaker,
)

from .config import APP_DATABASE_URL
from .services import utc_now

# Database connection
engine = create_engine(APP_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Models
class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class User(Base):
    """User model for multi-user support."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String, unique=True, nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    cities: Mapped[list[City]] = relationship(
        "City", back_populates="user", cascade="all, delete-orphan"
    )


class City(Base):
    """City model with forecast data stored as JSON."""

    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    forecast_data: Mapped[list[dict[str, Any]] | None] = mapped_column(
        JSON, nullable=True
    )
    forecast_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_user_city"),)

    user: Mapped[User] = relationship("User", back_populates="cities")


# Create tables
Base.metadata.create_all(bind=engine)


# Database dependency
def get_db() -> Iterator[Session]:
    """FastAPI dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

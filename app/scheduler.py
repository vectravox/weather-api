"""Background scheduler for updating weather forecasts.

This module manages automatic updates of weather forecasts for all tracked cities
using APScheduler.
"""

import asyncio

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session

from .config import (
    FORECAST_UPDATE_INTERVAL_MINUTES,
    JOBS_DATABASE_URL,
    OPEN_METEO_PARAMS,
    REQUEST_DELAY_SECONDS,
)
from .crud import update_city_forecast
from .database import City, SessionLocal
from .services import fetch_data, logger


async def update_forecasts() -> None:
    """Fetch and store hourly forecasts for all cities from Open-Meteo API."""
    db: Session = SessionLocal()

    try:
        cities = db.query(City).all()

        if not cities:
            return

        for city in cities:
            try:
                forecast_data = await fetch_data(
                    city.latitude,
                    city.longitude,
                    fetch_params=list(OPEN_METEO_PARAMS),
                    forecast_type="hourly",
                )
                update_city_forecast(db, city.id, forecast_data)
                logger.info(
                    f"--- Updated forecast for {city.name} for user_id: {city.user.id}"
                )
                await asyncio.sleep(REQUEST_DELAY_SECONDS)

            except Exception as e:
                logger.error(f"--- Failed to update forecast for {city.name}: {e}")

    finally:
        db.close()


def run_update_forecasts() -> None:
    """Wrap function for APScheduler."""
    asyncio.run(update_forecasts())


jobstores = {"default": SQLAlchemyJobStore(url=JOBS_DATABASE_URL)}


def start_scheduler() -> BackgroundScheduler:
    """Start the background scheduler for forecast updates."""
    scheduler = BackgroundScheduler(jobstores=jobstores)
    scheduler.add_job(
        run_update_forecasts,
        trigger=IntervalTrigger(minutes=FORECAST_UPDATE_INTERVAL_MINUTES),
        id="run_update_forecasts",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        f"--- Scheduler started. Forecasts will update every {FORECAST_UPDATE_INTERVAL_MINUTES} minutes."
    )
    return scheduler

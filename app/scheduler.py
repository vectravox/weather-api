"""Background scheduler for updating weather forecasts.

This module manages automatic updates of weather forecasts for all tracked cities
using APScheduler.
"""

import asyncio

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session

from . import config, crud
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
                    city.lat,
                    city.lon,
                    fetch_params=list(config.OPEN_METEO_PARAMS),
                    forecast_type="hourly",
                )
                crud.update_city_forecast(db, city.id, forecast_data)
                logger.info(
                    f"--- Updated forecast for {city.name} for user_id: {city.user.id}"
                )

                await asyncio.sleep(config.DELAY_BETWEEN_REQUESTS_SECONDS)

            except Exception as err:
                logger.error(f"--- Failed to update forecast for {city.name}: {err!r}")

    finally:
        db.close()


def run_update_forecasts() -> None:
    """Wrap function for APScheduler."""
    asyncio.run(update_forecasts())


jobstores = {"default": SQLAlchemyJobStore(url=config.SCHEDULER_DATABASE_URL)}


def start_scheduler() -> BackgroundScheduler:
    """Start the background scheduler for forecast updates."""
    scheduler = BackgroundScheduler(jobstores=jobstores)
    scheduler.add_job(
        run_update_forecasts,
        trigger=IntervalTrigger(minutes=config.FORECAST_UPDATE_INTERVAL_MINUTES),
        id="run_update_forecasts",
        replace_existing=True,
    )
    scheduler.start()
    return scheduler

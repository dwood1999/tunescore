"""Industry Pulse data collection wrapper."""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add backend/app to path so we can import the scraper
# This is needed because jobs/ is at the same level as app/
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal
from app.industry_snapshot.scraper import run_scraping_job

logger = logging.getLogger(__name__)


async def run_industry_pulse_job() -> None:
    """
    Wrapper to run the Industry Pulse scraping job.
    
    This wrapper manages the database session and error handling
    for the scheduled job.
    """
    logger.info("Starting Industry Pulse scheduled job")
    
    async with AsyncSessionLocal() as db:
        try:
            results = await run_scraping_job(db)
            logger.info(f"Industry Pulse job completed: {results}")
        except Exception as e:
            logger.error(f"Industry Pulse job failed: {e}")


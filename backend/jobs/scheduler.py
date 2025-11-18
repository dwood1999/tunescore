"""APScheduler job scheduler for background tasks.

Schedules and manages all background jobs.
"""

import asyncio
import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from artist_snapshots import collect_all_artist_snapshots
from viral_detection import detect_viral_signals

logger = logging.getLogger(__name__)


def setup_scheduler() -> AsyncIOScheduler:
    """
    Set up APScheduler with all jobs.

    Returns:
        Configured scheduler instance
    """
    scheduler = AsyncIOScheduler()

    # Artist snapshots - daily at 6:00 AM
    scheduler.add_job(
        collect_all_artist_snapshots,
        trigger=CronTrigger(hour=6, minute=0),
        id="artist_snapshots",
        name="Daily artist metrics snapshot collection",
        replace_existing=True,
    )
    logger.info("Scheduled: Artist snapshots (daily at 6:00 AM)")

    # Viral detection - every 4 hours
    scheduler.add_job(
        detect_viral_signals,
        trigger=CronTrigger(hour="*/4"),
        id="viral_detection",
        name="Viral signal detection (every 4 hours)",
        replace_existing=True,
    )
    logger.info("Scheduled: Viral detection (every 4 hours)")

    return scheduler


async def main() -> None:
    """Main entry point for the scheduler."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger.info("Starting TuneScore job scheduler")

    scheduler = setup_scheduler()
    scheduler.start()

    logger.info("Scheduler started. Press Ctrl+C to exit.")

    try:
        # Keep the scheduler running
        while True:
            await asyncio.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down scheduler")
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())


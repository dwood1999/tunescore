#!/usr/bin/env python3
"""Manual trigger for Industry Pulse data scraping job.

Run directly:
    python scripts/run_industry_scraper.py

Or via systemd timer (automated).
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal
from app.industry_snapshot.scraper import run_scraping_job

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/industry_scraper.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


async def main() -> None:
    """Run the scraping job."""
    logger.info("=" * 80)
    logger.info("Industry Pulse Data Scraper - Starting")
    logger.info("=" * 80)

    async with AsyncSessionLocal() as db:
        try:
            results = await run_scraping_job(db)

            logger.info("Scraping Results:")
            logger.info(f"  Spotify charts: {results['charts']['spotify']} entries")
            logger.info(f"  Billboard charts: {results['charts']['billboard']} entries")
            logger.info(f"  News articles: {results['news']} entries")
            logger.info(f"  New releases: {results['releases']} entries")
            logger.info(f"  Daily digest: {results['digest']}")

            if results["errors"]:
                logger.warning(f"Errors encountered: {len(results['errors'])}")
                for error in results["errors"]:
                    logger.warning(f"  - {error}")
            else:
                logger.info("No errors encountered")

            logger.info("=" * 80)
            logger.info("Industry Pulse Data Scraper - Complete")
            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"Scraping job failed: {e}", exc_info=True)
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())


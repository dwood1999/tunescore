"""Viral signal detection job.

Runs every 4 hours to detect early viral signals.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal
from app.services.prediction.viral_detector import ViralDetector

logger = logging.getLogger(__name__)


async def detect_viral_signals() -> dict[str, int]:
    """
    Scan tracks for viral signals.

    Returns:
        Dictionary with detection stats
    """
    logger.info("Starting viral signal detection job")

    async with AsyncSessionLocal() as db:
        detector = ViralDetector()

        # Scan recent tracks (last 100)
        results = await detector.scan_all_tracks(db, limit=100)

        logger.info(
            f"Viral detection complete: {results['tracks_scanned']} tracks scanned, "
            f"{results['alerts_created']} alerts created"
        )

        return results


async def main() -> None:
    """Main entry point for the job."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    stats = await detect_viral_signals()

    print("\n" + "=" * 60)
    print("Viral Signal Detection Complete")
    print("=" * 60)
    print(f"Tracks scanned: {stats['tracks_scanned']}")
    print(f"Alerts created: {stats['alerts_created']}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())


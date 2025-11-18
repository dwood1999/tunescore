"""Artist metrics snapshot collection job.

Runs daily to collect artist metrics from multiple platforms.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.track import Artist
from app.services.artist_intelligence.snapshot_collector import ArtistSnapshotCollector
from app.services.integrations.spotify import SpotifyClient

logger = logging.getLogger(__name__)


async def collect_all_artist_snapshots() -> dict[str, int]:
    """
    Collect snapshots for all tracked artists.

    Returns:
        Dictionary with collection stats
    """
    logger.info("Starting artist snapshot collection job")

    stats = {
        "artists_processed": 0,
        "snapshots_created": 0,
        "errors": 0,
    }

    async with AsyncSessionLocal() as db:
        try:
            # Get all artists with Spotify IDs
            result = await db.execute(
                select(Artist).where(Artist.spotify_id.isnot(None))
            )
            artists = result.scalars().all()

            logger.info(f"Found {len(artists)} artists to process")

            # Initialize collector
            spotify_client = SpotifyClient()
            collector = ArtistSnapshotCollector(spotify_client=spotify_client)

            # Process each artist
            for artist in artists:
                try:
                    # Collect Spotify snapshot
                    if artist.spotify_id:
                        snapshot_data = await collector.collect_spotify_snapshot(
                            artist.id, artist.spotify_id, db
                        )

                        if snapshot_data:
                            stats["snapshots_created"] += 1

                    stats["artists_processed"] += 1

                    # Rate limiting: small delay between requests
                    await asyncio.sleep(0.5)

                except Exception as e:
                    logger.error(f"Failed to collect snapshot for artist {artist.id}: {e}")
                    stats["errors"] += 1

            logger.info(
                f"Snapshot collection complete: {stats['snapshots_created']} snapshots created, "
                f"{stats['errors']} errors"
            )

        except Exception as e:
            logger.error(f"Snapshot collection job failed: {e}")
            stats["errors"] += 1

    return stats


async def main() -> None:
    """Main entry point for the job."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    stats = await collect_all_artist_snapshots()

    print("\n" + "=" * 60)
    print("Artist Snapshot Collection Complete")
    print("=" * 60)
    print(f"Artists processed: {stats['artists_processed']}")
    print(f"Snapshots created: {stats['snapshots_created']}")
    print(f"Errors: {stats['errors']}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())


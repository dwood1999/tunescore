"""Artist metrics snapshot collector extending SpotifyClient.

Collects daily snapshots of artist metrics across multiple platforms.
"""

import logging
from datetime import date, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ...models.track import Artist, ArtistMetricsSnapshot
from ..integrations.spotify import SpotifyClient

logger = logging.getLogger(__name__)


class ArtistSnapshotCollector:
    """
    Collect artist metrics snapshots from multiple platforms.

    Extends existing SpotifyClient for Spotify data, with hooks for
    YouTube, Instagram, TikTok integration.
    """

    def __init__(self, spotify_client: SpotifyClient | None = None) -> None:
        """
        Initialize snapshot collector.

        Args:
            spotify_client: Optional SpotifyClient instance
        """
        self.spotify_client = spotify_client or SpotifyClient()

    async def collect_spotify_snapshot(
        self, artist_id: int, spotify_artist_id: str, db: AsyncSession
    ) -> dict[str, Any] | None:
        """
        Collect Spotify metrics snapshot for an artist.

        Args:
            artist_id: Internal artist ID
            spotify_artist_id: Spotify artist ID
            db: Database session

        Returns:
            Snapshot data or None if failed
        """
        try:
            # Get artist data from Spotify
            sp = self.spotify_client.client
            artist_data = sp.artist(spotify_artist_id)

            # Extract metrics
            metrics = {
                "followers": artist_data.get("followers", {}).get("total", 0),
                "popularity": artist_data.get("popularity", 0),
                "genres": artist_data.get("genres", []),
                "images": artist_data.get("images", []),
            }

            # Get top tracks for additional metrics
            try:
                top_tracks = sp.artist_top_tracks(spotify_artist_id, country="US")
                tracks = top_tracks.get("tracks", [])
                if tracks:
                    avg_popularity = sum(t.get("popularity", 0) for t in tracks) / len(tracks)
                    metrics["avg_track_popularity"] = round(avg_popularity, 2)
                    metrics["top_tracks_count"] = len(tracks)
            except Exception as e:
                logger.warning(f"Failed to get top tracks: {e}")

            # Store snapshot
            snapshot = ArtistMetricsSnapshot(
                artist_id=artist_id,
                snapshot_date=date.today(),
                platform="spotify",
                metrics=metrics,
            )

            # Calculate velocity if previous snapshot exists
            await self._calculate_velocity(artist_id, "spotify", snapshot, db)

            db.add(snapshot)
            await db.commit()

            logger.info(
                f"Collected Spotify snapshot for artist {artist_id}: "
                f"{metrics.get('followers', 0)} followers"
            )

            return metrics

        except Exception as e:
            logger.error(f"Failed to collect Spotify snapshot for artist {artist_id}: {e}")
            return None

    async def collect_youtube_snapshot(
        self, artist_id: int, youtube_channel_id: str, db: AsyncSession
    ) -> dict[str, Any] | None:
        """
        Collect YouTube metrics snapshot for an artist.

        Args:
            artist_id: Internal artist ID
            youtube_channel_id: YouTube channel ID
            db: Database session

        Returns:
            Snapshot data or None if failed
        """
        # Placeholder for YouTube integration
        # Will use existing youtube_analytics.py patterns
        logger.info(f"YouTube snapshot collection not yet implemented for artist {artist_id}")
        return None

    async def collect_all_snapshots(self, artist_id: int, db: AsyncSession) -> dict[str, Any]:
        """
        Collect snapshots from all available platforms for an artist.

        Args:
            artist_id: Internal artist ID
            db: Database session

        Returns:
            Dictionary of platform: metrics
        """
        # Get artist data
        result = await db.execute(select(Artist).where(Artist.id == artist_id))
        artist = result.scalar_one_or_none()

        if not artist:
            logger.error(f"Artist {artist_id} not found")
            return {}

        snapshots = {}

        # Spotify
        if artist.spotify_id:
            spotify_data = await self.collect_spotify_snapshot(
                artist_id, artist.spotify_id, db
            )
            if spotify_data:
                snapshots["spotify"] = spotify_data

        # YouTube
        if artist.youtube_channel_id:
            youtube_data = await self.collect_youtube_snapshot(
                artist_id, artist.youtube_channel_id, db
            )
            if youtube_data:
                snapshots["youtube"] = youtube_data

        # Future: Instagram, TikTok
        # if artist.instagram_handle:
        #     instagram_data = await self.collect_instagram_snapshot(...)

        return snapshots

    async def _calculate_velocity(
        self,
        artist_id: int,
        platform: str,
        current_snapshot: ArtistMetricsSnapshot,
        db: AsyncSession,
    ) -> None:
        """
        Calculate 7-day and 28-day velocity based on previous snapshots.

        Args:
            artist_id: Artist ID
            platform: Platform name
            current_snapshot: Current snapshot to update
            db: Database session
        """
        try:
            # Get previous snapshots
            result = await db.execute(
                select(ArtistMetricsSnapshot)
                .where(
                    ArtistMetricsSnapshot.artist_id == artist_id,
                    ArtistMetricsSnapshot.platform == platform,
                )
                .order_by(ArtistMetricsSnapshot.snapshot_date.desc())
                .limit(30)  # Get last 30 days
            )
            previous_snapshots = result.scalars().all()

            if not previous_snapshots:
                return

            current_followers = current_snapshot.metrics.get("followers", 0)

            # 7-day velocity
            snapshot_7d = next(
                (
                    s
                    for s in previous_snapshots
                    if (date.today() - s.snapshot_date).days >= 7
                ),
                None,
            )
            if snapshot_7d:
                followers_7d = snapshot_7d.metrics.get("followers", 0)
                if followers_7d > 0:
                    velocity_7d = (current_followers - followers_7d) / followers_7d
                    current_snapshot.velocity_7d = round(velocity_7d, 4)

            # 28-day velocity
            snapshot_28d = next(
                (
                    s
                    for s in previous_snapshots
                    if (date.today() - s.snapshot_date).days >= 28
                ),
                None,
            )
            if snapshot_28d:
                followers_28d = snapshot_28d.metrics.get("followers", 0)
                if followers_28d > 0:
                    velocity_28d = (current_followers - followers_28d) / followers_28d
                    current_snapshot.velocity_28d = round(velocity_28d, 4)

            logger.info(
                f"Calculated velocity for artist {artist_id}: "
                f"7d={current_snapshot.velocity_7d}, 28d={current_snapshot.velocity_28d}"
            )

        except Exception as e:
            logger.error(f"Failed to calculate velocity: {e}")

    async def get_latest_metrics(
        self, artist_id: int, platform: str, db: AsyncSession
    ) -> dict[str, Any] | None:
        """
        Get latest metrics snapshot for an artist on a platform.

        Args:
            artist_id: Artist ID
            platform: Platform name
            db: Database session

        Returns:
            Latest metrics or None
        """
        result = await db.execute(
            select(ArtistMetricsSnapshot)
            .where(
                ArtistMetricsSnapshot.artist_id == artist_id,
                ArtistMetricsSnapshot.platform == platform,
            )
            .order_by(ArtistMetricsSnapshot.snapshot_date.desc())
            .limit(1)
        )
        snapshot = result.scalar_one_or_none()

        if snapshot:
            return {
                "metrics": snapshot.metrics,
                "velocity_7d": snapshot.velocity_7d,
                "velocity_28d": snapshot.velocity_28d,
                "snapshot_date": snapshot.snapshot_date.isoformat(),
            }

        return None

    async def get_metrics_history(
        self, artist_id: int, platform: str, days: int, db: AsyncSession
    ) -> list[dict[str, Any]]:
        """
        Get metrics history for an artist.

        Args:
            artist_id: Artist ID
            platform: Platform name
            days: Number of days to retrieve
            db: Database session

        Returns:
            List of snapshots ordered by date
        """
        result = await db.execute(
            select(ArtistMetricsSnapshot)
            .where(
                ArtistMetricsSnapshot.artist_id == artist_id,
                ArtistMetricsSnapshot.platform == platform,
            )
            .order_by(ArtistMetricsSnapshot.snapshot_date.desc())
            .limit(days)
        )
        snapshots = result.scalars().all()

        return [
            {
                "date": s.snapshot_date.isoformat(),
                "metrics": s.metrics,
                "velocity_7d": s.velocity_7d,
                "velocity_28d": s.velocity_28d,
            }
            for s in reversed(snapshots)  # Oldest first for charting
        ]


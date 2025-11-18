"""Viral signal detector for early trend detection.

Detects early signals of viral potential before tracks blow up.
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from ...models.track import Track, ViralAlert, ArtistMetricsSnapshot, PlaylistAppearance

logger = logging.getLogger(__name__)


class ViralDetector:
    """
    Detect early viral signals before tracks blow up.

    Signals:
    - Sudden playlist momentum
    - Velocity spikes
    - Social media mentions
    - TikTok usage
    """

    # Thresholds for viral alerts
    PLAYLIST_SPIKE_THRESHOLD = 5  # 5+ playlist adds in 24h
    VELOCITY_SPIKE_THRESHOLD = 0.15  # 15% growth in 7 days
    SOCIAL_SPIKE_THRESHOLD = 100  # 100+ social mentions in 24h
    CONFIDENCE_THRESHOLD = 0.70  # Only alert if confidence > 70%

    async def detect_viral_signals(
        self, track_id: int, db: AsyncSession
    ) -> list[dict[str, Any]]:
        """
        Detect viral signals for a track.

        Args:
            track_id: Track ID
            db: Database session

        Returns:
            List of detected signals
        """
        signals = []

        # Get track
        result = await db.execute(select(Track).where(Track.id == track_id))
        track = result.scalar_one_or_none()

        if not track:
            logger.warning(f"Track {track_id} not found")
            return signals

        # Check playlist momentum
        playlist_signal = await self._check_playlist_momentum(track_id, db)
        if playlist_signal:
            signals.append(playlist_signal)

        # Check artist velocity
        if track.artist_id:
            velocity_signal = await self._check_velocity_spike(track.artist_id, db)
            if velocity_signal:
                signals.append(velocity_signal)

        # Check social signals (placeholder - requires external data)
        # social_signal = await self._check_social_spike(track_id, db)

        return signals

    async def _check_playlist_momentum(
        self, track_id: int, db: AsyncSession
    ) -> dict[str, Any] | None:
        """Check for sudden playlist additions."""
        try:
            # Get playlist appearances in last 24 hours
            yesterday = datetime.utcnow() - timedelta(days=1)
            
            result = await db.execute(
                select(PlaylistAppearance)
                .where(
                    and_(
                        PlaylistAppearance.track_id == track_id,
                        PlaylistAppearance.added_at >= yesterday,
                    )
                )
            )
            recent_adds = result.scalars().all()

            if len(recent_adds) >= self.PLAYLIST_SPIKE_THRESHOLD:
                # Calculate total follower reach
                total_followers = sum(
                    p.playlist_followers or 0 for p in recent_adds
                )

                confidence = min(
                    0.95, 0.5 + (len(recent_adds) / 20)
                )  # More adds = higher confidence

                return {
                    "type": "playlist_momentum",
                    "confidence": confidence,
                    "description": f"Added to {len(recent_adds)} playlists in 24h (reach: {total_followers:,} followers)",
                    "details": {
                        "playlist_count": len(recent_adds),
                        "total_reach": total_followers,
                        "playlists": [
                            {
                                "name": p.playlist_name,
                                "followers": p.playlist_followers,
                                "type": p.playlist_type,
                            }
                            for p in recent_adds[:5]  # Top 5
                        ],
                    },
                }

            return None

        except Exception as e:
            logger.error(f"Error checking playlist momentum: {e}")
            return None

    async def _check_velocity_spike(
        self, artist_id: int, db: AsyncSession
    ) -> dict[str, Any] | None:
        """Check for sudden velocity spike in artist growth."""
        try:
            # Get recent snapshots
            result = await db.execute(
                select(ArtistMetricsSnapshot)
                .where(ArtistMetricsSnapshot.artist_id == artist_id)
                .order_by(ArtistMetricsSnapshot.snapshot_date.desc())
                .limit(2)
            )
            snapshots = result.scalars().all()

            if len(snapshots) < 2:
                return None

            latest = snapshots[0]

            # Check if velocity exceeds threshold
            if latest.velocity_7d and latest.velocity_7d >= self.VELOCITY_SPIKE_THRESHOLD:
                confidence = min(0.95, 0.6 + (latest.velocity_7d / 0.5))

                return {
                    "type": "velocity_spike",
                    "confidence": confidence,
                    "description": f"Artist growing at {latest.velocity_7d*100:.1f}% in 7 days on {latest.platform}",
                    "details": {
                        "platform": latest.platform,
                        "velocity_7d": latest.velocity_7d,
                        "velocity_28d": latest.velocity_28d,
                        "current_followers": latest.metrics.get("followers", 0),
                    },
                }

            return None

        except Exception as e:
            logger.error(f"Error checking velocity spike: {e}")
            return None

    async def create_viral_alerts(
        self, track_id: int, signals: list[dict[str, Any]], db: AsyncSession
    ) -> list[ViralAlert]:
        """
        Create viral alert records from detected signals.

        Args:
            track_id: Track ID
            signals: Detected signals
            db: Database session

        Returns:
            Created alert records
        """
        alerts = []

        for signal in signals:
            # Only create alerts for high-confidence signals
            if signal.get("confidence", 0) >= self.CONFIDENCE_THRESHOLD:
                alert = ViralAlert(
                    track_id=track_id,
                    alert_type=signal["type"],
                    confidence=signal["confidence"],
                    description=signal["description"],
                    triggered_at=datetime.utcnow(),
                    outcome="pending",
                )

                db.add(alert)
                alerts.append(alert)

                logger.info(
                    f"Viral alert created: {signal['type']} for track {track_id} "
                    f"(confidence: {signal['confidence']:.2f})"
                )

        if alerts:
            await db.commit()

        return alerts

    async def scan_all_tracks(self, db: AsyncSession, limit: int = 100) -> dict[str, Any]:
        """
        Scan all recent tracks for viral signals.

        Args:
            db: Database session
            limit: Maximum tracks to scan

        Returns:
            Scan summary
        """
        # Get recently added tracks
        result = await db.execute(
            select(Track).order_by(Track.created_at.desc()).limit(limit)
        )
        tracks = result.scalars().all()

        total_scanned = 0
        alerts_created = 0

        for track in tracks:
            signals = await self.detect_viral_signals(track.id, db)

            if signals:
                alerts = await self.create_viral_alerts(track.id, signals, db)
                alerts_created += len(alerts)

            total_scanned += 1

        logger.info(
            f"Viral scan complete: {total_scanned} tracks scanned, "
            f"{alerts_created} alerts created"
        )

        return {
            "tracks_scanned": total_scanned,
            "alerts_created": alerts_created,
            "scan_completed_at": datetime.utcnow().isoformat(),
        }

    async def get_recent_alerts(
        self, db: AsyncSession, days: int = 7, limit: int = 50
    ) -> list[dict[str, Any]]:
        """
        Get recent viral alerts.

        Args:
            db: Database session
            days: Number of days to look back
            limit: Maximum alerts to return

        Returns:
            List of recent alerts
        """
        cutoff = datetime.utcnow() - timedelta(days=days)

        result = await db.execute(
            select(ViralAlert)
            .where(ViralAlert.triggered_at >= cutoff)
            .order_by(ViralAlert.triggered_at.desc())
            .limit(limit)
        )
        alerts = result.scalars().all()

        return [
            {
                "id": alert.id,
                "track_id": alert.track_id,
                "alert_type": alert.alert_type,
                "confidence": alert.confidence,
                "description": alert.description,
                "triggered_at": alert.triggered_at.isoformat(),
                "outcome": alert.outcome,
            }
            for alert in alerts
        ]


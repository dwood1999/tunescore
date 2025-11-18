"""Credits fetcher using MusicBrainz API.

Fetches songwriter, producer, and contributor credits from MusicBrainz.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Try to import musicbrainzngs
MUSICBRAINZ_AVAILABLE = False
try:
    import musicbrainzngs as mb

    MUSICBRAINZ_AVAILABLE = True
    # Set user agent for MusicBrainz API
    mb.set_useragent("TuneScore", "0.1.0", "https://tunescore.app")
    logger.info("✅ MusicBrainz API client initialized")
except ImportError:
    logger.warning("⚠️ musicbrainzngs not available - credits fetching disabled")


class CreditsFetcher:
    """
    Fetch track credits from MusicBrainz API.

    MusicBrainz provides free, unlimited access to music metadata including
    credits, relationships, and recording details.
    """

    def __init__(self) -> None:
        """Initialize credits fetcher."""
        self.available = MUSICBRAINZ_AVAILABLE

    def search_recording(
        self, track_title: str, artist_name: str
    ) -> list[dict[str, Any]]:
        """
        Search for a recording on MusicBrainz.

        Args:
            track_title: Track title
            artist_name: Artist name

        Returns:
            List of matching recordings
        """
        if not self.available:
            logger.warning("MusicBrainz not available")
            return []

        try:
            # Search for recording
            result = mb.search_recordings(
                recording=track_title, artist=artist_name, limit=5
            )

            recordings = []
            for rec in result.get("recording-list", []):
                recordings.append(
                    {
                        "id": rec.get("id"),
                        "title": rec.get("title"),
                        "artist": rec.get("artist-credit-phrase", ""),
                        "score": rec.get("ext:score", 0),
                        "length": rec.get("length"),
                    }
                )

            logger.info(
                f"Found {len(recordings)} recordings for '{track_title}' by {artist_name}"
            )
            return recordings

        except Exception as e:
            logger.error(f"MusicBrainz search failed: {e}")
            return []

    def get_recording_credits(self, recording_id: str) -> dict[str, Any]:
        """
        Get detailed credits for a recording.

        Args:
            recording_id: MusicBrainz recording ID

        Returns:
            Dictionary with credits information
        """
        if not self.available:
            return {"available": False, "credits": []}

        try:
            # Get recording with relationships
            recording = mb.get_recording_by_id(
                recording_id, includes=["artists", "artist-rels", "work-rels"]
            )

            credits = []
            recording_data = recording.get("recording", {})

            # Extract artist relationships (producers, engineers, etc.)
            for rel in recording_data.get("artist-relation-list", []):
                artist = rel.get("artist", {})
                credits.append(
                    {
                        "name": artist.get("name"),
                        "role": rel.get("type"),
                        "type": "artist",
                        "mbid": artist.get("id"),
                    }
                )

            # Extract work relationships (composers, lyricists)
            for work_rel in recording_data.get("work-relation-list", []):
                work = work_rel.get("work", {})
                work_id = work.get("id")

                if work_id:
                    # Get work details for composer/lyricist info
                    try:
                        work_data = mb.get_work_by_id(
                            work_id, includes=["artist-rels"]
                        )
                        for artist_rel in (
                            work_data.get("work", {}).get("artist-relation-list", [])
                        ):
                            artist = artist_rel.get("artist", {})
                            credits.append(
                                {
                                    "name": artist.get("name"),
                                    "role": artist_rel.get("type"),
                                    "type": "work",
                                    "mbid": artist.get("id"),
                                }
                            )
                    except Exception as e:
                        logger.warning(f"Failed to get work details: {e}")

            logger.info(f"Found {len(credits)} credits for recording {recording_id}")

            return {
                "available": True,
                "recording_id": recording_id,
                "title": recording_data.get("title"),
                "credits": credits,
                "length": recording_data.get("length"),
            }

        except Exception as e:
            logger.error(f"Failed to get recording credits: {e}")
            return {"available": True, "error": str(e), "credits": []}

    def get_credits_by_search(
        self, track_title: str, artist_name: str
    ) -> dict[str, Any]:
        """
        Get credits by searching and fetching the best match.

        Args:
            track_title: Track title
            artist_name: Artist name

        Returns:
            Credits data
        """
        # Search for recording
        recordings = self.search_recording(track_title, artist_name)

        if not recordings:
            return {
                "available": True,
                "found": False,
                "credits": [],
            }

        # Get credits for best match (highest score)
        best_match = max(recordings, key=lambda x: x.get("score", 0))
        credits_data = self.get_recording_credits(best_match["id"])

        credits_data["found"] = True
        credits_data["match_score"] = best_match.get("score", 0)
        credits_data["matched_recording"] = best_match

        return credits_data

    def normalize_credits(self, credits: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Normalize credits to TuneScore format.

        Args:
            credits: Raw credits from MusicBrainz

        Returns:
            Normalized credits
        """
        role_mapping = {
            "composer": "songwriter",
            "lyricist": "songwriter",
            "writer": "songwriter",
            "producer": "producer",
            "engineer": "engineer",
            "mixer": "mixer",
            "mastering": "mastering engineer",
        }

        normalized = []
        for credit in credits:
            role = credit.get("role", "").lower()
            mapped_role = role_mapping.get(role, role)

            normalized.append(
                {
                    "contributor_name": credit.get("name"),
                    "role": mapped_role,
                    "source": "musicbrainz",
                    "source_id": credit.get("mbid"),
                }
            )

        return normalized


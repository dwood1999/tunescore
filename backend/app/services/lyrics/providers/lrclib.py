"""LRClib provider for free lyrics lookup."""

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class LRClibProvider:
    """
    Free lyrics lookup using LRClib.net API.
    
    LRClib is a community-driven lyrics database with no API key required.
    Coverage: Most popular songs in music history.
    """

    BASE_URL = "https://lrclib.net/api"
    TIMEOUT = 3.0  # seconds

    async def fetch_lyrics(
        self, 
        track_title: str, 
        artist_name: str,
        album_name: str | None = None,
        duration: float | None = None
    ) -> dict[str, Any] | None:
        """
        Fetch lyrics from LRClib.
        
        Args:
            track_title: Song title
            artist_name: Artist name
            album_name: Album name (optional, improves accuracy)
            duration: Track duration in seconds (optional, improves accuracy)
        
        Returns:
            {
                "text": str,           # Plain lyrics text
                "source": "lrclib",
                "confidence": 1.0,     # LRClib lyrics are human-verified
                "language": str,       # Detected language
                "synced": bool,        # Whether synced LRC is available
                "metadata": dict       # Additional metadata
            }
            or None if not found
        """
        try:
            # Build query parameters
            params = {
                "track_name": track_title.strip(),
                "artist_name": artist_name.strip(),
            }
            
            if album_name:
                params["album_name"] = album_name.strip()
            
            if duration:
                params["duration"] = int(duration)
            
            logger.info(
                f"Fetching lyrics from LRClib for '{track_title}' by '{artist_name}'"
            )
            
            # Make async request
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.get(f"{self.BASE_URL}/get", params=params)
                
                if response.status_code == 404:
                    logger.info("Lyrics not found in LRClib database")
                    return None
                
                if response.status_code != 200:
                    logger.warning(
                        f"LRClib API error: {response.status_code} - {response.text}"
                    )
                    return None
                
                data = response.json()
                
                # Extract plain text lyrics
                plain_lyrics = data.get("plainLyrics")
                synced_lyrics = data.get("syncedLyrics")
                
                if not plain_lyrics:
                    logger.info("LRClib returned empty lyrics")
                    return None
                
                logger.info(
                    f"✅ Successfully fetched lyrics from LRClib "
                    f"({len(plain_lyrics)} chars, synced: {bool(synced_lyrics)})"
                )
                
                # Build result
                result = {
                    "text": plain_lyrics.strip(),
                    "source": "lrclib",
                    "confidence": 1.0,  # LRClib is human-verified
                    "language": "en",  # LRClib is primarily English
                    "synced": bool(synced_lyrics),
                    "metadata": {
                        "lrclib_id": data.get("id"),
                        "track_name": data.get("trackName"),
                        "artist_name": data.get("artistName"),
                        "album_name": data.get("albumName"),
                        "duration": data.get("duration"),
                        "instrumental": data.get("instrumental", False),
                        "synced_lyrics": synced_lyrics if synced_lyrics else None,
                    }
                }
                
                return result
                
        except httpx.TimeoutException:
            logger.warning(f"LRClib request timed out after {self.TIMEOUT}s")
            return None
        except httpx.RequestError as e:
            logger.warning(f"LRClib request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching from LRClib: {e}")
            return None


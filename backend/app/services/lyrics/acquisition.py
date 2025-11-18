"""Lyrics acquisition orchestrator with multi-source support."""

import logging
from typing import Any

from .providers.lrclib import LRClibProvider
from ..audio.transcription import get_transcriber

logger = logging.getLogger(__name__)


class LyricsAcquisition:
    """
    Orchestrate lyrics acquisition from multiple sources.
    
    Priority:
    1. Return provided_lyrics if present (user-provided)
    2. Try LRClib if title+artist available (instant, free, accurate)
    3. Fall back to Whisper transcription (local, free, 85-95% accurate)
    """

    def __init__(self):
        """Initialize lyrics acquisition with providers."""
        self.lrclib = LRClibProvider()

    async def get_lyrics(
        self,
        audio_path: str | None = None,
        track_title: str | None = None,
        artist_name: str | None = None,
        album_name: str | None = None,
        duration: float | None = None,
        provided_lyrics: str | None = None,
        whisper_model_size: str = "small"
    ) -> dict[str, Any]:
        """
        Acquire lyrics from the best available source.
        
        Args:
            audio_path: Path to audio file (required for transcription)
            track_title: Track title (required for LRClib lookup)
            artist_name: Artist name (required for LRClib lookup)
            album_name: Album name (optional, improves LRClib accuracy)
            duration: Track duration in seconds (optional, improves LRClib accuracy)
            provided_lyrics: User-provided lyrics text (highest priority)
            whisper_model_size: Whisper model size for transcription
        
        Returns:
            {
                "text": str,                # Lyrics text (empty if all methods fail)
                "source": str,              # "user", "lrclib", "whisper", or "none"
                "confidence": float,        # 0.0-1.0
                "language": str | None,     # Detected language
                "metadata": dict,           # Source-specific metadata
                "success": bool             # Whether lyrics were obtained
            }
        """
        # Tier 1: Use provided lyrics (highest priority)
        if provided_lyrics and provided_lyrics.strip():
            logger.info("Using user-provided lyrics")
            return {
                "text": provided_lyrics.strip(),
                "source": "user",
                "confidence": 1.0,
                "language": None,  # Not detected for user-provided
                "metadata": {},
                "success": True,
            }

        # Tier 2: Try LRClib lookup (instant, accurate)
        if track_title and artist_name:
            logger.info("Attempting LRClib lyrics lookup...")
            try:
                lrclib_result = await self.lrclib.fetch_lyrics(
                    track_title=track_title,
                    artist_name=artist_name,
                    album_name=album_name,
                    duration=duration
                )
                
                if lrclib_result and lrclib_result.get("text"):
                    logger.info("✅ Successfully obtained lyrics from LRClib")
                    return {
                        "text": lrclib_result["text"],
                        "source": "lrclib",
                        "confidence": lrclib_result["confidence"],
                        "language": lrclib_result.get("language"),
                        "metadata": lrclib_result.get("metadata", {}),
                        "success": True,
                    }
                else:
                    logger.info("LRClib lookup returned no results")
                    
            except Exception as e:
                logger.warning(f"LRClib lookup failed: {e}")

        # Tier 3: Fall back to Whisper transcription
        if audio_path:
            logger.info(f"Falling back to Whisper transcription (model: {whisper_model_size})...")
            try:
                transcriber = get_transcriber(model_size=whisper_model_size)
                transcription = transcriber.transcribe_lyrics(str(audio_path))
                
                if transcription["success"] and transcription["text"]:
                    logger.info(
                        f"✅ Successfully transcribed lyrics with Whisper "
                        f"(confidence: {transcription['confidence']:.2f})"
                    )
                    return {
                        "text": transcription["text"],
                        "source": "whisper",
                        "confidence": transcription["confidence"],
                        "language": transcription.get("language"),
                        "metadata": {
                            "segments": transcription.get("segments", []),
                            "model_size": whisper_model_size,
                        },
                        "success": True,
                    }
                else:
                    logger.warning("Whisper transcription failed or returned empty text")
                    
            except Exception as e:
                logger.error(f"Whisper transcription error: {e}")

        # All methods failed
        logger.warning("All lyrics acquisition methods failed")
        return {
            "text": "",
            "source": "none",
            "confidence": 0.0,
            "language": None,
            "metadata": {},
            "success": False,
        }


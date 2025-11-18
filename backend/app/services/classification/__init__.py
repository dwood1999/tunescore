"""Classification services for genre, mood, etc."""

from .genre_detector import detect_genre, detect_genre_hybrid

__all__ = ["detect_genre", "detect_genre_hybrid"]


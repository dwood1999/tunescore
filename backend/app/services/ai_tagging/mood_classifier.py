"""Mood classification from sonic and lyrical features.

Classifies track moods using existing analysis data (sonic_genome + lyrical_genome).
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class MoodClassifier:
    """
    Classify track moods using sonic and lyrical features.

    Uses rule-based mapping of energy, valence, tempo, and sentiment
    to mood labels.
    """

    def classify(
        self, sonic_genome: dict[str, Any], lyrical_genome: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Classify track mood.

        Args:
            sonic_genome: Sonic analysis features
            lyrical_genome: Lyrical analysis features (optional)

        Returns:
            Dictionary with mood classifications
        """
        # Extract key features
        energy = sonic_genome.get("energy", 0.5)
        valence = sonic_genome.get("valence", 0.5)
        tempo = sonic_genome.get("tempo", 120)
        acousticness = sonic_genome.get("acousticness", 0.5)

        # Lyrical sentiment if available
        sentiment = 0.0
        if lyrical_genome:
            compound_sentiment = lyrical_genome.get("sentiment", {}).get("compound", 0.0)
            # Normalize VADER compound (-1 to 1) to (0 to 1)
            sentiment = (compound_sentiment + 1.0) / 2.0

        # Mood classification using Russell's circumplex model
        # Energy (arousal) vs Valence (pleasantness)
        moods = []
        mood_scores = {}

        # High energy + positive valence
        if energy > 0.6 and valence > 0.6:
            moods.append("energetic")
            moods.append("uplifting")
            mood_scores["energetic"] = round((energy + valence) / 2, 3)

            if tempo > 130:
                moods.append("euphoric")
                mood_scores["euphoric"] = round((energy + valence + (tempo / 200)) / 3, 3)

        # High energy + negative valence
        if energy > 0.6 and valence < 0.4:
            moods.append("aggressive")
            moods.append("intense")
            mood_scores["aggressive"] = round((energy + (1 - valence)) / 2, 3)

            if sentiment < 0.3:
                moods.append("angry")
                mood_scores["angry"] = round((energy + (1 - valence) + (1 - sentiment)) / 3, 3)

        # Low energy + positive valence
        if energy < 0.4 and valence > 0.6:
            moods.append("calm")
            moods.append("peaceful")
            mood_scores["calm"] = round(((1 - energy) + valence) / 2, 3)

            if acousticness > 0.6:
                moods.append("serene")
                mood_scores["serene"] = round(((1 - energy) + valence + acousticness) / 3, 3)

        # Low energy + negative valence
        if energy < 0.4 and valence < 0.4:
            moods.append("melancholic")
            moods.append("sad")
            mood_scores["melancholic"] = round(((1 - energy) + (1 - valence)) / 2, 3)

            if sentiment < 0.3:
                moods.append("depressing")
                mood_scores["depressing"] = round(
                    ((1 - energy) + (1 - valence) + (1 - sentiment)) / 3, 3
                )

        # Mid-range energy + positive valence
        if 0.4 <= energy <= 0.6 and valence > 0.5:
            moods.append("cheerful")
            mood_scores["cheerful"] = round((energy + valence) / 2, 3)

        # Mid-range energy + negative valence
        if 0.4 <= energy <= 0.6 and valence < 0.5:
            moods.append("introspective")
            mood_scores["introspective"] = round(((1 - valence) + 0.5) / 2, 3)

        # Tempo-based moods
        if tempo > 140:
            if "energetic" not in moods:
                moods.append("fast-paced")
                mood_scores["fast-paced"] = round(tempo / 200, 3)
        elif tempo < 80:
            if "calm" not in moods:
                moods.append("slow")
                mood_scores["slow"] = round((120 - tempo) / 120, 3)

        # Acousticness-based
        if acousticness > 0.7:
            moods.append("acoustic")
            mood_scores["acoustic"] = round(acousticness, 3)
            moods.append("organic")
            mood_scores["organic"] = round(acousticness, 3)

        # Remove duplicates while preserving order
        moods = list(dict.fromkeys(moods))

        # Sort by score
        sorted_moods = sorted(mood_scores.items(), key=lambda x: x[1], reverse=True)

        return {
            "moods": moods[:5],  # Top 5 moods
            "mood_scores": dict(sorted_moods[:5]),
            "primary_mood": sorted_moods[0][0] if sorted_moods else "neutral",
            "energy_level": self._energy_level(energy),
            "valence_level": self._valence_level(valence),
        }

    def classify_commercial_tags(self, sonic_genome: dict[str, Any]) -> list[str]:
        """
        Generate commercial tags (radio-friendly, sync-ready, etc.).

        Args:
            sonic_genome: Sonic analysis features

        Returns:
            List of commercial tags
        """
        tags = []

        energy = sonic_genome.get("energy", 0.5)
        valence = sonic_genome.get("valence", 0.5)
        tempo = sonic_genome.get("tempo", 120)
        acousticness = sonic_genome.get("acousticness", 0.5)
        speechiness = sonic_genome.get("speechiness", 0.5)

        # Radio-friendly: mid-high energy, positive valence, commercial tempo
        if energy > 0.5 and valence > 0.5 and 100 <= tempo <= 140:
            tags.append("radio-friendly")

        # Sync-ready: high production quality, clear structure
        production_quality = sonic_genome.get("timing_precision_score", 0)
        if production_quality > 0.7:
            tags.append("sync-ready")

        # Playlist-worthy: streaming-optimized
        if energy > 0.4 and valence > 0.4:
            tags.append("playlist-worthy")

        # Dancefloor: high energy + tempo
        if energy > 0.7 and tempo > 120:
            tags.append("dancefloor")

        # Chill/background: low energy, mid valence
        if energy < 0.4 and 0.4 < valence < 0.7:
            tags.append("chill")
            tags.append("background-music")

        # Minimal vocals (good for sync)
        if speechiness < 0.3:
            tags.append("instrumental-friendly")

        # Acoustic/organic
        if acousticness > 0.6:
            tags.append("organic-sound")

        return tags

    def _energy_level(self, energy: float) -> str:
        """Convert energy score to categorical level."""
        if energy > 0.7:
            return "high"
        elif energy > 0.4:
            return "medium"
        else:
            return "low"

    def _valence_level(self, valence: float) -> str:
        """Convert valence score to categorical level."""
        if valence > 0.6:
            return "positive"
        elif valence > 0.4:
            return "neutral"
        else:
            return "negative"


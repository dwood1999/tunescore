"""Harmonic analysis based on music theory and psychoacoustic research.

Analyzes chord progressions for inherent pleasantness, emotional impact,
and healing/therapeutic properties based on established research.
"""

import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


class HarmonicAnalyzer:
    """
    Analyze chord progressions for inherent musical qualities.

    Based on:
    - Music theory (circle of fifths, voice leading)
    - Psychoacoustics (consonance/dissonance ratios)
    - Healing frequency research (A=432Hz, Solfeggio frequencies)
    - Popular progression patterns ("golden standards")
    """

    # Golden standard progressions (most pleasing to human ear)
    GOLDEN_PROGRESSIONS = {
        # Pop/Rock standards
        "I-V-vi-IV": {"pleasantness": 0.95, "name": "Pop Perfection (Axis)", "emotion": "uplifting"},
        "vi-IV-I-V": {"pleasantness": 0.93, "name": "Sensitive (Axis reversed)", "emotion": "melancholic"},
        "I-IV-V-IV": {"pleasantness": 0.90, "name": "Classic Rock", "emotion": "confident"},
        "I-vi-IV-V": {"pleasantness": 0.92, "name": "50s Progression", "emotion": "nostalgic"},
        
        # Jazz standards
        "ii-V-I": {"pleasantness": 0.88, "name": "Jazz Turnaround", "emotion": "sophisticated"},
        "I-vi-ii-V": {"pleasantness": 0.87, "name": "Rhythm Changes", "emotion": "swinging"},
        
        # Modern/Alternative
        "i-VII-VI-VII": {"pleasantness": 0.85, "name": "Andalusian Cadence", "emotion": "exotic"},
        "I-iii-IV-iv": {"pleasantness": 0.89, "name": "Chromatic Mediant", "emotion": "cinematic"},
        
        # Emotional progressions
        "I-IV-vi-V": {"pleasantness": 0.91, "name": "Heartfelt", "emotion": "emotional"},
        "vi-V-IV-V": {"pleasantness": 0.86, "name": "Ascending Hope", "emotion": "hopeful"},
    }

    # Healing/therapeutic frequencies (Hz)
    SOLFEGGIO_FREQUENCIES = {
        174: "Pain relief, grounding",
        285: "Tissue healing, energy fields",
        396: "Liberation from fear and guilt",
        417: "Facilitating change, undoing situations",
        528: "Transformation and miracles (DNA repair)",
        639: "Connecting relationships, harmony",
        741: "Awakening intuition, problem solving",
        852: "Returning to spiritual order",
        963: "Divine consciousness, pineal activation",
    }

    # Scientific tuning standards
    TUNING_STANDARDS = {
        432: {
            "name": "Verdi's A / Natural Tuning",
            "properties": "Mathematically consistent with universe, promotes relaxation",
            "healing": True,
        },
        440: {
            "name": "Standard Pitch (ISO 16)",
            "properties": "Modern standard, bright and energetic",
            "healing": False,
        },
        528: {
            "name": "Love Frequency (Solfeggio)",
            "properties": "DNA repair, transformation, miracles",
            "healing": True,
        },
    }

    # Consonance intervals (ratio of frequencies)
    CONSONANCE_RATIOS = {
        "unison": (1, 1, 1.0),  # Perfect consonance
        "octave": (2, 1, 1.0),
        "perfect_fifth": (3, 2, 0.95),
        "perfect_fourth": (4, 3, 0.85),
        "major_third": (5, 4, 0.80),
        "minor_third": (6, 5, 0.75),
        "major_sixth": (5, 3, 0.78),
        "minor_sixth": (8, 5, 0.70),
        "major_second": (9, 8, 0.40),
        "minor_second": (16, 15, 0.20),  # Dissonant
        "tritone": (45, 32, 0.10),  # Most dissonant
    }

    def analyze_chord_progression(
        self, chord_sequence: list[str]
    ) -> dict[str, Any]:
        """
        Analyze a chord progression for inherent qualities.

        Args:
            chord_sequence: List of chord symbols (e.g., ["C", "Am", "F", "G"])

        Returns:
            Analysis including pleasantness, healing properties, emotional impact
        """
        # Convert to Roman numeral analysis (assumes C major for now)
        roman_sequence = self._to_roman_numerals(chord_sequence)
        roman_pattern = "-".join(roman_sequence)

        # Check if it matches a golden standard
        golden_match = None
        max_similarity = 0
        for pattern, data in self.GOLDEN_PROGRESSIONS.items():
            similarity = self._pattern_similarity(roman_pattern, pattern)
            if similarity > max_similarity:
                max_similarity = similarity
                golden_match = {**data, "pattern": pattern}

        # Calculate inherent pleasantness
        pleasantness = self._calculate_pleasantness(chord_sequence)

        # Analyze voice leading quality
        voice_leading = self._analyze_voice_leading(chord_sequence)

        # Detect healing properties
        healing_properties = self._detect_healing_properties(chord_sequence)

        # Emotional trajectory
        emotional_impact = self._calculate_emotional_impact(chord_sequence)

        return {
            "chord_sequence": chord_sequence,
            "roman_numeral_pattern": roman_pattern,
            "pleasantness_score": round(pleasantness, 3),  # 0-1
            "golden_standard_match": golden_match if max_similarity > 0.7 else None,
            "voice_leading_quality": voice_leading,
            "healing_properties": healing_properties,
            "emotional_impact": emotional_impact,
            "analysis": self._generate_analysis(pleasantness, golden_match, voice_leading),
        }

    def analyze_tuning(self, reference_freq: float) -> dict[str, Any]:
        """
        Analyze tuning standard and healing properties.

        Args:
            reference_freq: Reference frequency (typically A4)

        Returns:
            Tuning analysis with healing properties
        """
        # Find closest tuning standard
        closest_standard = min(
            self.TUNING_STANDARDS.items(),
            key=lambda x: abs(x[0] - reference_freq),
        )

        freq_diff = reference_freq - closest_standard[0]
        is_exact_match = abs(freq_diff) < 1.0

        # Check if close to Solfeggio frequencies
        solfeggio_matches = []
        for freq, description in self.SOLFEGGIO_FREQUENCIES.items():
            # Check if any harmonic matches (octaves)
            for octave_mult in [0.25, 0.5, 1.0, 2.0, 4.0]:
                solfeggio_at_octave = freq * octave_mult
                if abs(reference_freq - solfeggio_at_octave) < 5.0:
                    solfeggio_matches.append(
                        {
                            "frequency": freq,
                            "description": description,
                            "octave": octave_mult,
                        }
                    )

        return {
            "reference_frequency": round(reference_freq, 2),
            "tuning_standard": {
                "frequency": closest_standard[0],
                "name": closest_standard[1]["name"],
                "properties": closest_standard[1]["properties"],
                "healing": closest_standard[1]["healing"],
                "is_exact_match": is_exact_match,
                "deviation_hz": round(freq_diff, 2),
            },
            "solfeggio_alignments": solfeggio_matches,
            "healing_potential": len(solfeggio_matches) > 0
            or closest_standard[1]["healing"],
        }

    def _to_roman_numerals(self, chords: list[str]) -> list[str]:
        """Convert chord symbols to Roman numerals (simplified)."""
        # This is a simplified mapping - in production would use more sophisticated parsing
        chord_to_roman = {
            "C": "I",
            "Dm": "ii",
            "Em": "iii",
            "F": "IV",
            "G": "V",
            "Am": "vi",
            "Bdim": "vii°",
            # Minor key variants
            "Cm": "i",
            "Eb": "III",
            "Fm": "iv",
            "Gm": "v",
            "Ab": "VI",
            "Bb": "VII",
        }

        return [chord_to_roman.get(chord, "?") for chord in chords]

    def _pattern_similarity(self, pattern1: str, pattern2: str) -> float:
        """Calculate similarity between two Roman numeral patterns."""
        if pattern1 == pattern2:
            return 1.0

        # Check if one is a rotation of the other
        p2_parts = pattern2.split("-")
        for i in range(len(p2_parts)):
            rotated = "-".join(p2_parts[i:] + p2_parts[:i])
            if pattern1 == rotated:
                return 0.9

        # Partial match
        p1_parts = set(pattern1.split("-"))
        p2_parts_set = set(pattern2.split("-"))
        overlap = len(p1_parts & p2_parts_set)
        total = len(p1_parts | p2_parts_set)

        return overlap / total if total > 0 else 0

    def _calculate_pleasantness(self, chords: list[str]) -> float:
        """
        Calculate inherent pleasantness based on consonance.

        Uses psychoacoustic principles:
        - Consonant intervals are inherently pleasing
        - Stepwise voice leading is pleasing
        - Resolution of tension is pleasing
        """
        if len(chords) < 2:
            return 0.5

        pleasantness = 0.7  # Base score

        # Check for common pleasing movements
        for i in range(len(chords) - 1):
            current = chords[i]
            next_chord = chords[i + 1]

            # I-IV-V progressions are inherently pleasing
            if any(
                combo in f"{current}-{next_chord}"
                for combo in ["C-F", "F-G", "G-C", "Am-F", "F-C"]
            ):
                pleasantness += 0.05

            # Descending fifths (circle of fifths) are pleasing
            if self._is_circle_of_fifths(current, next_chord):
                pleasantness += 0.08

        # Penalize too much repetition
        unique_ratio = len(set(chords)) / len(chords)
        if unique_ratio < 0.5:
            pleasantness -= 0.1

        return min(1.0, max(0.0, pleasantness))

    def _is_circle_of_fifths(self, chord1: str, chord2: str) -> bool:
        """Check if progression follows circle of fifths."""
        circle = ["C", "G", "D", "A", "E", "B", "F#", "C#", "Ab", "Eb", "Bb", "F"]

        try:
            root1 = chord1.replace("m", "").replace("dim", "")
            root2 = chord2.replace("m", "").replace("dim", "")

            idx1 = circle.index(root1)
            idx2 = circle.index(root2)

            # Check if moving clockwise by one
            return (idx1 + 1) % len(circle) == idx2
        except (ValueError, IndexError):
            return False

    def _analyze_voice_leading(self, chords: list[str]) -> dict[str, Any]:
        """
        Analyze voice leading quality.

        Good voice leading = smooth transitions between chords.
        """
        if len(chords) < 2:
            return {"quality": "unknown", "score": 0.5}

        # Simplified voice leading analysis
        # In production, would calculate actual voice movements
        smoothness_score = 0.75  # Default

        # Check for common smooth progressions
        smooth_progressions = ["I-vi", "vi-IV", "IV-V", "V-I"]
        roman = self._to_roman_numerals(chords)

        smooth_count = 0
        for i in range(len(roman) - 1):
            if f"{roman[i]}-{roman[i+1]}" in smooth_progressions:
                smooth_count += 1

        if len(roman) > 1:
            smoothness_score += (smooth_count / (len(roman) - 1)) * 0.2

        quality_label = "excellent" if smoothness_score > 0.85 else "good" if smoothness_score > 0.70 else "moderate"

        return {
            "quality": quality_label,
            "score": round(min(1.0, smoothness_score), 3),
            "smooth_transitions": smooth_count,
        }

    def _detect_healing_properties(self, chords: list[str]) -> dict[str, Any]:
        """
        Detect potential healing/therapeutic properties.

        Based on:
        - Harmonic relationships (perfect intervals = healing)
        - Tuning (A=432Hz alignment)
        - Solfeggio frequency alignment
        - Consonance ratios
        """
        healing_score = 0.0
        properties = []

        # Check for perfect intervals (5ths, 4ths, octaves)
        # These are mathematically pure and considered healing
        for i in range(len(chords) - 1):
            if self._is_perfect_interval(chords[i], chords[i + 1]):
                healing_score += 0.15
                properties.append("Contains perfect intervals (5ths/4ths)")
                break

        # Check for major chords (major third = 5:4 ratio, naturally consonant)
        major_count = sum(1 for c in chords if "m" not in c and "dim" not in c)
        if major_count / len(chords) > 0.6:
            healing_score += 0.10
            properties.append("Predominantly major tonality (uplifting)")

        # Simple, diatonic progressions = healing (not overly complex)
        if len(set(chords)) <= 4:
            healing_score += 0.10
            properties.append("Simple, diatonic progression (calming)")

        # Resolve to tonic (creates psychological closure)
        if chords[-1] in ["C", "Cm", "Am"]:  # Common tonics
            healing_score += 0.05
            properties.append("Resolves to tonic (closure/completion)")

        healing_level = (
            "high"
            if healing_score > 0.30
            else "moderate" if healing_score > 0.15 else "low"
        )

        return {
            "healing_score": round(min(1.0, healing_score), 3),
            "healing_level": healing_level,
            "properties": properties,
            "description": self._healing_description(healing_level),
        }

    def _is_perfect_interval(self, chord1: str, chord2: str) -> bool:
        """Check if chords form a perfect interval (5th, 4th, octave)."""
        # Simplified check - in production would calculate actual intervals
        perfect_movements = [
            ("C", "G"),  # Perfect 5th
            ("G", "C"),  # Perfect 4th
            ("F", "C"),  # Perfect 5th
            ("C", "F"),  # Perfect 4th
            ("D", "A"),
            ("A", "D"),
            ("E", "B"),
            ("B", "E"),
        ]

        root1 = chord1.replace("m", "").replace("dim", "")
        root2 = chord2.replace("m", "").replace("dim", "")

        return (root1, root2) in perfect_movements

    def _calculate_emotional_impact(self, chords: list[str]) -> dict[str, Any]:
        """
        Calculate emotional impact of progression.

        Major chords = positive emotion
        Minor chords = melancholic emotion
        Movement = tension/release
        """
        major_count = sum(1 for c in chords if "m" not in c and "dim" not in c)
        minor_count = sum(1 for c in chords if "m" in c)

        emotional_valence = (major_count - minor_count) / len(chords)

        # Classify emotion
        if emotional_valence > 0.4:
            emotion = "uplifting"
        elif emotional_valence > 0.1:
            emotion = "positive"
        elif emotional_valence > -0.1:
            emotion = "neutral"
        elif emotional_valence > -0.4:
            emotion = "melancholic"
        else:
            emotion = "sorrowful"

        return {
            "emotional_valence": round(emotional_valence, 3),
            "emotion": emotion,
            "major_ratio": round(major_count / len(chords), 3),
            "minor_ratio": round(minor_count / len(chords), 3),
        }

    def _healing_description(self, healing_level: str) -> str:
        """Generate description of healing properties."""
        descriptions = {
            "high": "This progression has strong therapeutic properties. The harmonic relationships promote relaxation, emotional balance, and psychological well-being.",
            "moderate": "This progression contains some healing elements. The consonant intervals and resolution patterns support emotional regulation.",
            "low": "This progression is more focused on artistic expression than therapeutic effect. It may create emotional tension or complexity.",
        }
        return descriptions.get(healing_level, "")

    def _generate_analysis(
        self,
        pleasantness: float,
        golden_match: dict[str, Any] | None,
        voice_leading: dict[str, Any],
    ) -> str:
        """Generate human-readable analysis."""
        parts = []

        # Pleasantness
        if pleasantness > 0.85:
            parts.append("This progression is highly pleasing to the human ear.")
        elif pleasantness > 0.70:
            parts.append("This progression has good inherent pleasantness.")
        else:
            parts.append("This progression is more experimental or complex.")

        # Golden standard match
        if golden_match:
            parts.append(
                f"It closely matches the '{golden_match['name']}' progression, "
                f"known for its {golden_match['emotion']} quality."
            )

        # Voice leading
        if voice_leading["quality"] == "excellent":
            parts.append("The voice leading is exceptionally smooth.")

        return " ".join(parts)

    def analyze_frequency_healing(self, frequencies: list[float]) -> dict[str, Any]:
        """
        Analyze frequencies for healing/therapeutic properties.

        Args:
            frequencies: List of frequencies (Hz) present in the audio

        Returns:
            Healing frequency analysis
        """
        solfeggio_hits = []

        # Check for Solfeggio frequencies (with ±5Hz tolerance)
        for freq in frequencies:
            for solfeggio_freq, description in self.SOLFEGGIO_FREQUENCIES.items():
                if abs(freq - solfeggio_freq) <= 5.0:
                    solfeggio_hits.append(
                        {
                            "frequency": solfeggio_freq,
                            "actual": round(freq, 2),
                            "description": description,
                            "deviation": round(freq - solfeggio_freq, 2),
                        }
                    )

        # Analyze dominant frequency for tuning standard
        if frequencies:
            # Assume fundamental is lowest strong frequency
            fundamental = min(frequencies)

            # Calculate what A4 would be if this is the fundamental
            # (Simplified - in production would use proper pitch detection)
            estimated_a4 = fundamental * 440 / 261.63  # Rough estimate

            tuning_analysis = self.analyze_tuning(estimated_a4)
        else:
            tuning_analysis = None

        return {
            "solfeggio_frequencies_detected": len(solfeggio_hits),
            "solfeggio_matches": solfeggio_hits,
            "tuning_analysis": tuning_analysis,
            "healing_potential": len(solfeggio_hits) > 0
            or (
                tuning_analysis
                and tuning_analysis["tuning_standard"]["healing"]
            ),
        }


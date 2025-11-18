"""Chord progression analysis using librosa chroma features."""

import logging
from collections import Counter
from typing import Any

import librosa
import numpy as np

logger = logging.getLogger(__name__)


class ChordAnalyzer:
    """Analyze chord progressions using chroma-based detection."""

    # Common chord progressions in popular music
    COMMON_PROGRESSIONS = {
        "I-V-vi-IV": "Pop progression (very common)",
        "I-IV-V": "Classic rock progression",
        "vi-IV-I-V": "Sensitive progression",
        "I-vi-IV-V": "50s progression (doo-wop)",
        "ii-V-I": "Jazz turnaround",
        "I-V-vi-iii-IV-I-IV-V": "Canon progression",
        "I-IV-I-V": "Simple folk progression",
        "vi-IV-V": "Minor pop progression",
    }

    # Chord templates (major and minor triads)
    CHORD_TEMPLATES = {
        # Major chords
        "C": [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
        "C#": [0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
        "D": [0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0],
        "D#": [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0],
        "E": [0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1],
        "F": [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0],
        "F#": [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0],
        "G": [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
        "G#": [1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
        "A": [0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
        "A#": [0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0],
        "B": [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1],
        # Minor chords
        "Cm": [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
        "C#m": [0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
        "Dm": [0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0],
        "D#m": [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0],
        "Em": [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
        "Fm": [1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
        "F#m": [0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0],
        "Gm": [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0],
        "G#m": [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1],
        "Am": [1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
        "A#m": [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0],
        "Bm": [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    }

    def __init__(self, sample_rate: int = 22050):
        """
        Initialize chord analyzer.

        Args:
            sample_rate: Target sample rate for audio processing
        """
        self.sample_rate = sample_rate

    def analyze(self, audio_path: str) -> dict[str, Any]:
        """
        Analyze chord progression from audio.

        Args:
            audio_path: Path to audio file

        Returns:
            Dictionary containing chord analysis
        """
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=self.sample_rate, mono=True)

            # Extract chromagram
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=2048)

            # Detect chords from chromagram
            chords = self._detect_chords(chroma, sr)

            # Detect key and mode
            key, mode = self._detect_key(chroma)

            # Analyze progression
            chord_sequence = [c["chord"] for c in chords]
            unique_chords = len(set(chord_sequence))

            # Identify progression pattern
            progression_name, progression_description = self._identify_progression(
                chord_sequence, key
            )

            # Calculate complexity
            harmonic_complexity = self._calculate_complexity(
                chord_sequence, unique_chords, chroma
            )

            # Familiarity vs novelty
            familiarity_score = self._calculate_familiarity(
                progression_name, chord_sequence
            )
            novelty_score = 100 - familiarity_score

            # Detect modulations (key changes)
            modulations = self._detect_modulations(chords, chroma, sr)

            # Generate recommendations
            recommendations = self._generate_recommendations(
                progression_name,
                harmonic_complexity,
                familiarity_score,
                modulations,
                unique_chords,
            )

            return {
                "chords": chords[:50],  # Limit to first 50 chords for response size
                "key": f"{key} {mode}",
                "chord_sequence": chord_sequence[:20],  # First 20 chords
                "unique_chords": unique_chords,
                "progression_name": progression_name,
                "progression_description": progression_description,
                "harmonic_complexity": round(harmonic_complexity, 1),
                "familiarity_score": round(familiarity_score, 1),
                "novelty_score": round(novelty_score, 1),
                "modulations": modulations,
                "recommendations": recommendations,
            }

        except Exception as e:
            logger.error(f"Failed to analyze chords for {audio_path}: {e}")
            raise

    def _detect_chords(
        self, chroma: np.ndarray, sr: int, hop_length: int = 2048
    ) -> list[dict[str, Any]]:
        """
        Detect chords from chromagram using template matching.

        Args:
            chroma: Chromagram
            sr: Sample rate
            hop_length: Hop length for time conversion

        Returns:
            List of detected chords with timestamps
        """
        chords = []
        frames_per_second = sr / hop_length

        # Analyze in 2-second windows
        window_size = int(2 * frames_per_second)

        for i in range(0, chroma.shape[1], window_size // 2):  # 50% overlap
            window = chroma[:, i : i + window_size]
            if window.shape[1] < window_size // 2:
                break

            # Average chroma over window
            avg_chroma = np.mean(window, axis=1)

            # Normalize
            avg_chroma = avg_chroma / (np.sum(avg_chroma) + 1e-8)

            # Match against chord templates
            best_chord = self._match_chord_template(avg_chroma)

            # Calculate confidence
            confidence = self._calculate_chord_confidence(avg_chroma, best_chord)

            # Time in seconds
            time = i / frames_per_second

            chords.append(
                {
                    "time": round(time, 1),
                    "chord": best_chord,
                    "confidence": round(confidence, 2),
                    "duration": 2.0,
                }
            )

        return chords

    def _match_chord_template(self, chroma: np.ndarray) -> str:
        """
        Match chroma vector against chord templates.

        Args:
            chroma: Normalized chroma vector

        Returns:
            Best matching chord name
        """
        best_chord = "N"  # No chord
        best_score = 0

        for chord_name, template in self.CHORD_TEMPLATES.items():
            # Cosine similarity
            template_array = np.array(template)
            score = np.dot(chroma, template_array) / (
                np.linalg.norm(chroma) * np.linalg.norm(template_array) + 1e-8
            )

            if score > best_score:
                best_score = score
                best_chord = chord_name

        return best_chord

    def _calculate_chord_confidence(self, chroma: np.ndarray, chord: str) -> float:
        """Calculate confidence score for detected chord."""
        if chord == "N" or chord not in self.CHORD_TEMPLATES:
            return 0.0

        template = np.array(self.CHORD_TEMPLATES[chord])
        # Cosine similarity
        confidence = np.dot(chroma, template) / (
            np.linalg.norm(chroma) * np.linalg.norm(template) + 1e-8
        )

        return float(np.clip(confidence, 0, 1))

    def _detect_key(self, chroma: np.ndarray) -> tuple[str, str]:
        """
        Detect key and mode from chromagram.

        Args:
            chroma: Chromagram

        Returns:
            Tuple of (key, mode)
        """
        # Average chroma over entire track
        avg_chroma = np.mean(chroma, axis=1)

        # Detect key (most prominent pitch class)
        key_index = int(np.argmax(avg_chroma))
        keys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        key = keys[key_index]

        # Detect mode (major vs minor) using profile correlation
        major_profile = np.array([1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1])
        minor_profile = np.array([1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0])

        # Rotate profiles to match detected key
        major_rotated = np.roll(major_profile, key_index)
        minor_rotated = np.roll(minor_profile, key_index)

        # Correlate with average chroma
        major_corr = np.corrcoef(avg_chroma, major_rotated)[0, 1]
        minor_corr = np.corrcoef(avg_chroma, minor_rotated)[0, 1]

        mode = "major" if major_corr > minor_corr else "minor"

        return key, mode

    def _identify_progression(
        self, chord_sequence: list[str], key: str
    ) -> tuple[str, str]:
        """
        Identify common chord progression patterns.

        Args:
            chord_sequence: List of chord names
            key: Detected key

        Returns:
            Tuple of (progression_name, description)
        """
        # Simplify sequence (remove consecutive duplicates)
        simplified = []
        for chord in chord_sequence:
            if not simplified or chord != simplified[-1]:
                simplified.append(chord)

        # Check for common 4-chord progressions
        if len(simplified) >= 4:
            # Extract first 4 unique chords
            four_chords = simplified[:4]

            # Check against common patterns (simplified matching)
            for pattern_name, description in self.COMMON_PROGRESSIONS.items():
                # Simple heuristic: if key chord appears first, might be this progression
                if key in four_chords[0]:
                    if len(four_chords) == 4:
                        return pattern_name, description

        return "Custom progression", "Unique chord progression"

    def _calculate_complexity(
        self, chord_sequence: list[str], unique_chords: int, chroma: np.ndarray
    ) -> float:
        """
        Calculate harmonic complexity score (0-100).

        Args:
            chord_sequence: List of chords
            unique_chords: Number of unique chords
            chroma: Chromagram

        Returns:
            Complexity score
        """
        # 1. Unique chord diversity (0-40 points)
        if unique_chords <= 3:
            diversity_score = 10
        elif unique_chords <= 5:
            diversity_score = 20
        elif unique_chords <= 8:
            diversity_score = 30
        else:
            diversity_score = 40

        # 2. Chord change frequency (0-30 points)
        if len(chord_sequence) > 1:
            changes = sum(
                1 for i in range(len(chord_sequence) - 1) if chord_sequence[i] != chord_sequence[i + 1]
            )
            change_rate = changes / len(chord_sequence)
            frequency_score = min(change_rate * 60, 30)
        else:
            frequency_score = 0

        # 3. Harmonic richness from chroma (0-30 points)
        # More active pitch classes = more complex
        avg_chroma = np.mean(chroma, axis=1)
        active_pitches = np.sum(avg_chroma > 0.1)  # Threshold for "active"
        richness_score = min((active_pitches / 12) * 30, 30)

        return diversity_score + frequency_score + richness_score

    def _calculate_familiarity(
        self, progression_name: str, chord_sequence: list[str]
    ) -> float:
        """
        Calculate familiarity score (0-100).

        Args:
            progression_name: Identified progression name
            chord_sequence: List of chords

        Returns:
            Familiarity score (higher = more familiar)
        """
        # Known progressions are highly familiar
        if progression_name in self.COMMON_PROGRESSIONS:
            return 85.0

        # Count common chords
        common_chords = ["C", "G", "Am", "F", "D", "Em", "A", "E", "Dm", "Bm"]
        if not chord_sequence:
            return 50.0

        common_count = sum(
            1 for chord in chord_sequence if any(c in chord for c in common_chords)
        )

        return (common_count / len(chord_sequence)) * 100

    def _detect_modulations(
        self, chords: list[dict[str, Any]], chroma: np.ndarray, sr: int
    ) -> list[dict[str, Any]]:
        """
        Detect key changes (modulations) in the progression.

        Args:
            chords: List of detected chords
            chroma: Chromagram
            sr: Sample rate

        Returns:
            List of modulations
        """
        modulations = []

        # Analyze in segments
        segment_length = len(chords) // 4 if len(chords) >= 4 else len(chords)

        if segment_length < 2:
            return modulations

        prev_key = None
        prev_mode = None

        for i in range(0, len(chords), segment_length):
            segment_chords = chords[i : i + segment_length]
            if not segment_chords:
                continue

            # Get chroma for this segment
            start_frame = int(segment_chords[0]["time"] * sr / 2048)
            end_frame = int(segment_chords[-1]["time"] * sr / 2048)
            segment_chroma = chroma[:, start_frame:end_frame]

            if segment_chroma.shape[1] == 0:
                continue

            # Detect key for this segment
            key, mode = self._detect_key(segment_chroma)

            if prev_key is not None and (key != prev_key or mode != prev_mode):
                modulations.append(
                    {
                        "time": segment_chords[0]["time"],
                        "from_key": f"{prev_key} {prev_mode}",
                        "to_key": f"{key} {mode}",
                    }
                )

            prev_key = key
            prev_mode = mode

        return modulations

    def _generate_recommendations(
        self,
        progression_name: str,
        complexity: float,
        familiarity: float,
        modulations: list[dict[str, Any]],
        unique_chords: int,
    ) -> list[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Complexity recommendations
        if complexity < 30:
            recommendations.append(
                "Try adding more chord variety or extensions (7ths, 9ths) to increase harmonic interest."
            )
        elif complexity > 70:
            recommendations.append(
                "Your progression is harmonically complex. Ensure it serves the song's emotional arc."
            )

        # Familiarity recommendations
        if familiarity > 80:
            recommendations.append(
                f"You're using a very common progression. Consider adding a unique twist or unexpected chord."
            )
        elif familiarity < 30:
            recommendations.append(
                "Your progression is highly unique. Ensure it's memorable and supports the melody."
            )

        # Chord variety
        if unique_chords <= 3:
            recommendations.append(
                "Limited chord variety detected. Consider adding a bridge with different chords."
            )

        # Modulation recommendations
        if len(modulations) == 0:
            recommendations.append(
                "No key changes detected. Consider a modulation for the bridge or final chorus to add interest."
            )
        elif len(modulations) > 3:
            recommendations.append(
                "Multiple key changes detected. Ensure transitions feel natural and intentional."
            )

        return recommendations


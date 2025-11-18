"""Advanced hook detection for viral segments using madmom.

Identifies 15-second segments optimized for TikTok/Reels/Shorts.
Uses madmom for precise onset/beat detection and novelty analysis.
"""

import logging
from typing import Any

import librosa
import numpy as np

logger = logging.getLogger(__name__)

# Try to import madmom (optional dependency)
MADMOM_AVAILABLE = False
try:
    import madmom

    MADMOM_AVAILABLE = True
    logger.info("✅ Madmom loaded successfully for advanced hook detection")
except ImportError:
    logger.warning(
        "⚠️ Madmom not available - using librosa-only hook detection. "
        "Install with: pip install madmom"
    )


class ViralHookDetector:
    """
    Detect viral hook segments optimized for social media (15-second clips).

    Uses madmom for onset detection and beat tracking when available,
    falls back to librosa otherwise.
    """

    def __init__(self, sample_rate: int = 22050) -> None:
        """
        Initialize viral hook detector.

        Args:
            sample_rate: Target sample rate
        """
        self.sample_rate = sample_rate
        self.use_madmom = MADMOM_AVAILABLE

    def detect_viral_segments(
        self, audio_path: str, segment_duration: float = 15.0, top_n: int = 3
    ) -> dict[str, Any]:
        """
        Detect top viral hook segments.

        Args:
            audio_path: Path to audio file
            segment_duration: Target duration for each segment (default 15s)
            top_n: Number of top segments to return

        Returns:
            Dictionary with viral segments and scores
        """
        if self.use_madmom:
            return self._detect_with_madmom(audio_path, segment_duration, top_n)
        else:
            return self._detect_with_librosa(audio_path, segment_duration, top_n)

    def _detect_with_madmom(
        self, audio_path: str, segment_duration: float, top_n: int
    ) -> dict[str, Any]:
        """
        Detect viral segments using madmom.

        Args:
            audio_path: Path to audio file
            segment_duration: Segment duration in seconds
            top_n: Number of segments to return

        Returns:
            Viral segment analysis with madmom precision
        """
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=self.sample_rate, mono=True)
            duration = librosa.get_duration(y=y, sr=sr)

            # Madmom onset detection (more precise than librosa)
            onset_proc = madmom.features.onsets.OnsetPeakPickingProcessor(
                fps=100, threshold=0.5
            )
            onset_act = madmom.features.onsets.RNNOnsetProcessor()(audio_path)
            onsets = onset_proc(onset_act)

            # Beat tracking with madmom
            beat_proc = madmom.features.beats.BeatTrackingProcessor(fps=100)
            beat_act = madmom.features.beats.RNNBeatProcessor()(audio_path)
            beats = beat_proc(beat_act)

            # Novelty detection
            novelty = self._compute_novelty(y, sr)

            # Energy envelope
            energy = librosa.feature.rms(y=y)[0]

            # Score segments
            segments = self._score_segments(
                y, sr, duration, onsets, beats, novelty, energy, segment_duration
            )

            # Return top N segments
            top_segments = sorted(segments, key=lambda x: x["score"], reverse=True)[
                :top_n
            ]

            return {
                "provider": "madmom",
                "segment_duration": segment_duration,
                "total_segments_analyzed": len(segments),
                "viral_segments": top_segments,
                "onsets_count": len(onsets),
                "beats_count": len(beats),
            }

        except Exception as e:
            logger.error(f"Madmom detection failed: {e}, falling back to librosa")
            return self._detect_with_librosa(audio_path, segment_duration, top_n)

    def _detect_with_librosa(
        self, audio_path: str, segment_duration: float, top_n: int
    ) -> dict[str, Any]:
        """
        Detect viral segments using librosa.

        Args:
            audio_path: Path to audio file
            segment_duration: Segment duration in seconds
            top_n: Number of segments to return

        Returns:
            Viral segment analysis with librosa
        """
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=self.sample_rate, mono=True)
            duration = librosa.get_duration(y=y, sr=sr)

            # Onset detection
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            onsets = librosa.onset.onset_detect(
                onset_envelope=onset_env, sr=sr, units="time"
            )

            # Beat tracking
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            beat_times = librosa.frames_to_time(beats, sr=sr)

            # Novelty
            novelty = self._compute_novelty(y, sr)

            # Energy
            energy = librosa.feature.rms(y=y)[0]

            # Score segments
            segments = self._score_segments(
                y, sr, duration, onsets, beat_times, novelty, energy, segment_duration
            )

            # Return top N
            top_segments = sorted(segments, key=lambda x: x["score"], reverse=True)[
                :top_n
            ]

            return {
                "provider": "librosa",
                "segment_duration": segment_duration,
                "total_segments_analyzed": len(segments),
                "viral_segments": top_segments,
                "onsets_count": len(onsets),
                "beats_count": len(beat_times),
            }

        except Exception as e:
            logger.error(f"Librosa detection failed: {e}")
            return {
                "provider": "none",
                "error": str(e),
                "viral_segments": [],
            }

    def _score_segments(
        self,
        y: np.ndarray,
        sr: int,
        duration: float,
        onsets: np.ndarray,
        beats: np.ndarray,
        novelty: np.ndarray,
        energy: np.ndarray,
        segment_duration: float,
    ) -> list[dict[str, Any]]:
        """
        Score all possible segments for viral potential.

        Args:
            y: Audio signal
            sr: Sample rate
            duration: Total duration
            onsets: Onset times
            beats: Beat times
            novelty: Novelty curve
            energy: Energy envelope
            segment_duration: Target segment duration

        Returns:
            List of scored segments
        """
        segments = []
        hop_length = 512  # For frame-to-time conversions
        segment_samples = int(segment_duration * sr)

        # Slide window through track (1-second steps)
        step = sr  # 1 second
        for start_sample in range(0, len(y) - segment_samples, step):
            end_sample = start_sample + segment_samples
            start_time = start_sample / sr
            end_time = end_sample / sr

            # Extract segment
            segment = y[start_sample:end_sample]

            # Calculate scores
            onset_score = self._calculate_onset_density(
                onsets, start_time, end_time
            )
            beat_score = self._calculate_beat_quality(beats, start_time, end_time)
            energy_score = self._calculate_energy_score(
                energy, start_sample, end_sample, hop_length
            )
            novelty_score = self._calculate_novelty_score(
                novelty, start_sample, end_sample, hop_length
            )
            hook_score = self._calculate_hook_memorability(segment, sr)

            # Weighted composite score
            composite_score = (
                onset_score * 0.15
                + beat_score * 0.20
                + energy_score * 0.25
                + novelty_score * 0.20
                + hook_score * 0.20
            )

            # Bonus for ideal placement (not at very start or end)
            if 15 < start_time < duration - 30:
                composite_score *= 1.1

            segments.append(
                {
                    "start_time": round(start_time, 2),
                    "end_time": round(end_time, 2),
                    "duration": segment_duration,
                    "score": round(composite_score * 100, 1),  # 0-100 scale
                    "factors": {
                        "onset_density": round(onset_score * 100, 1),
                        "beat_quality": round(beat_score * 100, 1),
                        "energy": round(energy_score * 100, 1),
                        "novelty": round(novelty_score * 100, 1),
                        "hook_memorability": round(hook_score * 100, 1),
                    },
                    "reasons": self._generate_reasons(
                        onset_score, beat_score, energy_score, novelty_score, hook_score
                    ),
                }
            )

        return segments

    def _calculate_onset_density(
        self, onsets: np.ndarray, start: float, end: float
    ) -> float:
        """Calculate onset density in segment (more onsets = more interesting)."""
        segment_onsets = onsets[(onsets >= start) & (onsets < end)]
        density = len(segment_onsets) / (end - start)
        # Normalize: 5-10 onsets per second is good
        return min(1.0, density / 7.0)

    def _calculate_beat_quality(
        self, beats: np.ndarray, start: float, end: float
    ) -> float:
        """Calculate beat quality (strong, regular beats = more danceable)."""
        segment_beats = beats[(beats >= start) & (beats < end)]
        if len(segment_beats) < 2:
            return 0.0

        # Beat regularity
        beat_intervals = np.diff(segment_beats)
        regularity = 1.0 - (np.std(beat_intervals) / (np.mean(beat_intervals) + 1e-6))

        return max(0.0, min(1.0, regularity))

    def _calculate_energy_score(
        self, energy: np.ndarray, start_sample: int, end_sample: int, hop_length: int
    ) -> float:
        """Calculate energy score (high energy = more engaging)."""
        start_frame = start_sample // hop_length
        end_frame = end_sample // hop_length
        segment_energy = energy[start_frame:end_frame]

        if len(segment_energy) == 0:
            return 0.0

        # Normalize by max energy in track
        normalized_energy = np.mean(segment_energy) / (np.max(energy) + 1e-6)
        return min(1.0, normalized_energy)

    def _calculate_novelty_score(
        self, novelty: np.ndarray, start_sample: int, end_sample: int, hop_length: int
    ) -> float:
        """Calculate novelty score (new elements = more interesting)."""
        start_frame = start_sample // hop_length
        end_frame = end_sample // hop_length
        segment_novelty = novelty[start_frame:end_frame]

        if len(segment_novelty) == 0:
            return 0.0

        return min(1.0, np.mean(segment_novelty))

    def _calculate_hook_memorability(self, segment: np.ndarray, sr: int) -> float:
        """
        Calculate hook memorability (melodic repetition + pitch clarity).
        """
        try:
            # Pitch tracking
            pitches, magnitudes = librosa.piptrack(y=segment, sr=sr)

            # Get dominant pitch over time
            pitch_track = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_track.append(pitch)

            if len(pitch_track) < 10:
                return 0.0

            # Pitch consistency (more consistent = more memorable)
            pitch_std = np.std(pitch_track)
            pitch_mean = np.mean(pitch_track)
            consistency = 1.0 - (pitch_std / (pitch_mean + 1e-6))

            # Normalize to 0-1
            return max(0.0, min(1.0, consistency))

        except Exception:
            return 0.5  # Default

    def _compute_novelty(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Compute spectral novelty curve."""
        spec = np.abs(librosa.stft(y))
        novelty = librosa.onset.onset_strength(S=librosa.amplitude_to_db(spec, ref=np.max))
        # Normalize
        novelty = (novelty - np.min(novelty)) / (np.max(novelty) - np.min(novelty) + 1e-6)
        return novelty

    def _generate_reasons(
        self,
        onset_score: float,
        beat_score: float,
        energy_score: float,
        novelty_score: float,
        hook_score: float,
    ) -> list[str]:
        """Generate human-readable reasons for segment selection."""
        reasons = []

        if onset_score > 0.7:
            reasons.append("High onset density - dynamic and engaging")
        if beat_score > 0.7:
            reasons.append("Strong, regular beat - highly danceable")
        if energy_score > 0.7:
            reasons.append("High energy peak - grabs attention")
        if novelty_score > 0.7:
            reasons.append("Novel elements - fresh and interesting")
        if hook_score > 0.7:
            reasons.append("Memorable melodic hook - easy to sing along")

        # Fallbacks
        if not reasons:
            if energy_score > 0.5:
                reasons.append("Good energy level")
            if beat_score > 0.5:
                reasons.append("Decent rhythm")
            if not reasons:
                reasons.append("Accessible entry point")

        return reasons


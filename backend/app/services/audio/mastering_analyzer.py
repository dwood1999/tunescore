"""Mastering quality analysis using LUFS and Dynamic Range metering."""

import logging
from typing import Any

import librosa
import numpy as np
import pyloudnorm as pyln

logger = logging.getLogger(__name__)


class MasteringAnalyzer:
    """Analyze mastering quality using industry-standard LUFS and DR metering."""

    def __init__(self, sample_rate: int = 22050):
        """
        Initialize mastering analyzer.

        Args:
            sample_rate: Target sample rate for audio processing
        """
        self.sample_rate = sample_rate
        self.meter = pyln.Meter(sample_rate)  # BS.1770 meter

    def analyze(self, audio_path: str) -> dict[str, Any]:
        """
        Analyze mastering quality of an audio file.

        Args:
            audio_path: Path to audio file

        Returns:
            Dictionary containing mastering quality metrics
        """
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=self.sample_rate, mono=True)

            # 1. LUFS measurement (integrated loudness)
            lufs = self.meter.integrated_loudness(y)

            # 2. Peak level (dBFS)
            peak_db = 20 * np.log10(np.max(np.abs(y)))

            # 3. RMS level (dBFS)
            rms = np.sqrt(np.mean(y**2))
            rms_db = 20 * np.log10(rms + 1e-8)

            # 4. Dynamic Range (DR) score
            dynamic_range = self._calculate_dr_score(y)

            # 5. Platform target comparison
            platform_targets = self._compare_platform_targets(lufs)

            # 6. Overall quality score (0-100)
            overall_quality = self._calculate_quality_score(lufs, peak_db, dynamic_range)

            # 7. Recommendations
            recommendations = self._generate_recommendations(
                lufs, peak_db, dynamic_range, platform_targets
            )

            return {
                "lufs": round(lufs, 1),
                "lufs_grade": self._get_lufs_grade(lufs),
                "peak_db": round(peak_db, 1),
                "rms_db": round(rms_db, 1),
                "dynamic_range": round(dynamic_range, 1),
                "dr_grade": self._get_dr_grade(dynamic_range),
                "platform_targets": platform_targets,
                "overall_quality": round(overall_quality, 1),
                "quality_grade": self._get_quality_grade(overall_quality),
                "recommendations": recommendations,
            }

        except Exception as e:
            logger.error(f"Failed to analyze mastering quality for {audio_path}: {e}")
            raise

    def _calculate_dr_score(self, y: np.ndarray) -> float:
        """
        Calculate Dynamic Range score (DR meter standard).

        Args:
            y: Audio signal

        Returns:
            Dynamic Range score in dB
        """
        # Split into 3-second segments
        segment_length = self.sample_rate * 3
        segments = [
            y[i : i + segment_length]
            for i in range(0, len(y), segment_length)
            if len(y[i : i + segment_length]) == segment_length
        ]

        if not segments:
            return 0.0

        # Calculate DR for each segment
        dr_values = []
        for segment in segments:
            peak = np.max(np.abs(segment))
            seg_rms = np.sqrt(np.mean(segment**2))
            if seg_rms > 0:
                dr = 20 * np.log10(peak / seg_rms)
                dr_values.append(dr)

        # Return median DR (robust to outliers)
        return float(np.median(dr_values)) if dr_values else 0.0

    def _compare_platform_targets(self, lufs: float) -> dict[str, dict[str, Any]]:
        """
        Compare LUFS to streaming platform targets.

        Args:
            lufs: Measured LUFS value

        Returns:
            Dictionary of platform targets with deltas and status
        """
        targets = {
            "spotify": -14,
            "apple_music": -16,
            "youtube": -13,
            "tidal": -14,
            "soundcloud": -10,
        }

        results = {}
        for platform, target in targets.items():
            delta = lufs - target

            if abs(delta) <= 1:
                status = "optimal"
            elif delta > 1:
                status = "too_loud"
            else:
                status = "too_quiet"

            results[platform] = {
                "target": target,
                "delta": round(delta, 1),
                "status": status,
            }

        return results

    def _calculate_quality_score(
        self, lufs: float, peak_db: float, dr: float
    ) -> float:
        """
        Calculate overall mastering quality score (0-100).

        Args:
            lufs: LUFS value
            peak_db: Peak level in dBFS
            dr: Dynamic Range score

        Returns:
            Quality score (0-100)
        """
        # 1. LUFS score (optimal: -14 to -10 LUFS)
        if -14 <= lufs <= -10:
            lufs_score = 100
        elif -16 <= lufs < -14:
            lufs_score = 80 + (lufs + 16) * 10
        elif -10 < lufs <= -8:
            lufs_score = 80 + (10 - lufs) * 10
        elif -20 <= lufs < -16:
            lufs_score = 60 + (lufs + 20) * 5
        else:
            lufs_score = 40

        # 2. Peak score (optimal: -0.5 to -0.1 dBFS)
        if -0.5 <= peak_db <= -0.1:
            peak_score = 100
        elif -1.0 <= peak_db < -0.5:
            peak_score = 80
        elif peak_db > -0.1:
            peak_score = 50  # Clipping risk
        else:
            peak_score = 60  # Too much headroom

        # 3. DR score (optimal: 8-14 DR)
        if 8 <= dr <= 14:
            dr_score = 100
        elif 6 <= dr < 8:
            dr_score = 70  # Over-compressed
        elif 14 < dr <= 18:
            dr_score = 80  # Natural dynamics
        elif dr < 6:
            dr_score = 40  # Severely over-compressed (loudness war)
        else:
            dr_score = 60  # Too dynamic (under-compressed)

        # Weighted average
        return (lufs_score * 0.4) + (peak_score * 0.3) + (dr_score * 0.3)

    def _get_lufs_grade(self, lufs: float) -> str:
        """Convert LUFS to grade."""
        if -14 <= lufs <= -10:
            return "Optimal"
        if -16 <= lufs < -14:
            return "Slightly Quiet"
        if -10 < lufs <= -8:
            return "Slightly Loud"
        if lufs < -16:
            return "Too Quiet"
        return "Too Loud"

    def _get_dr_grade(self, dr: float) -> str:
        """Convert DR to grade."""
        if dr >= 14:
            return "Excellent Dynamics"
        if dr >= 10:
            return "Good Dynamics"
        if dr >= 8:
            return "Acceptable"
        if dr >= 6:
            return "Over-Compressed"
        return "Severely Over-Compressed"

    def _get_quality_grade(self, score: float) -> str:
        """Convert quality score to grade."""
        if score >= 90:
            return "Professional"
        if score >= 75:
            return "Good"
        if score >= 60:
            return "Acceptable"
        if score >= 45:
            return "Needs Improvement"
        return "Poor"

    def _generate_recommendations(
        self,
        lufs: float,
        peak_db: float,
        dr: float,
        platform_targets: dict[str, dict[str, Any]],
    ) -> list[str]:
        """
        Generate actionable recommendations.

        Args:
            lufs: LUFS value
            peak_db: Peak level
            dr: Dynamic Range
            platform_targets: Platform target comparison

        Returns:
            List of recommendations
        """
        recommendations = []

        # LUFS recommendations
        if lufs < -16:
            recommendations.append(
                "Track is too quiet. Apply makeup gain or use a limiter to increase loudness."
            )
        elif lufs > -8:
            recommendations.append(
                "Track is too loud. Reduce limiting/compression to avoid distortion."
            )

        # Peak recommendations
        if peak_db > -0.1:
            recommendations.append(
                "Peak level is too high (clipping risk). Leave at least -0.3 dBFS headroom."
            )
        elif peak_db < -2.0:
            recommendations.append(
                "Peak level is too low. You have excessive headroom—increase output level."
            )

        # DR recommendations
        if dr < 6:
            recommendations.append(
                "Dynamic range is too low (loudness war territory). Reduce compression/limiting."
            )
        elif dr > 18:
            recommendations.append(
                "Dynamic range is very high. Consider gentle compression for streaming."
            )

        # Platform-specific recommendations
        spotify_status = platform_targets["spotify"]["status"]
        if spotify_status == "too_loud":
            recommendations.append(
                "Spotify will turn down your track. Target -14 LUFS for optimal loudness."
            )
        elif spotify_status == "too_quiet":
            recommendations.append(
                "Spotify will turn up your track (adding noise). Increase loudness to -14 LUFS."
            )

        return recommendations


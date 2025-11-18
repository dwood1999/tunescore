"""Audio feature extraction using librosa."""

import logging
from typing import Any

import librosa
import numpy as np

from .spectral_advanced import AdvancedSpectralAnalyzer

logger = logging.getLogger(__name__)


class AudioFeatureExtractor:
    """Extract audio features using librosa."""

    def __init__(self, sample_rate: int = 22050):
        """
        Initialize audio feature extractor.

        Args:
            sample_rate: Target sample rate for audio processing
        """
        self.sample_rate = sample_rate
        self.spectral_analyzer = AdvancedSpectralAnalyzer(sample_rate=sample_rate)

    def load_audio(self, file_path: str) -> tuple[np.ndarray, int]:
        """
        Load audio file.

        Args:
            file_path: Path to audio file

        Returns:
            Tuple of (audio data, sample rate)
        """
        import subprocess
        from pathlib import Path
        
        file_path_obj = Path(file_path)
        file_ext = file_path_obj.suffix.lower()
        
        # Check if FFmpeg is needed for this format
        formats_requiring_ffmpeg = {'.m4a', '.aac', '.mp4'}
        
        try:
            y, sr = librosa.load(file_path, sr=self.sample_rate, mono=True)
            return y, sr
        except Exception as e:
            error_msg = str(e)
            
            # Check if FFmpeg is missing for formats that need it
            if file_ext in formats_requiring_ffmpeg:
                # Check if FFmpeg is available
                try:
                    subprocess.run(['ffmpeg', '-version'], 
                                 capture_output=True, 
                                 timeout=2,
                                 check=True)
                    ffmpeg_available = True
                except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                    ffmpeg_available = False
                
                if not ffmpeg_available:
                    logger.error(
                        f"Failed to load {file_ext} file {file_path}: FFmpeg is required for {file_ext} files. "
                        f"Install with: sudo apt-get install -y ffmpeg"
                    )
                    raise RuntimeError(
                        f"Audio format {file_ext} requires FFmpeg to be installed. "
                        f"Please install FFmpeg: sudo apt-get install -y ffmpeg"
                    ) from e
            
            logger.error(f"Failed to load audio file {file_path}: {error_msg}")
            raise

    def extract_sonic_genome(self, audio_path: str) -> dict[str, Any]:
        """
        Extract comprehensive sonic features (Sonic DNA).

        Args:
            audio_path: Path to audio file

        Returns:
            Dictionary containing sonic genome features
        """
        y, sr = self.load_audio(audio_path)

        # Duration
        duration = librosa.get_duration(y=y, sr=sr)

        # Tempo and beat tracking
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)

        # Key and mode detection (using chroma features)
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        key = int(np.argmax(np.sum(chroma, axis=1)))

        # Spectral features
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]

        # Zero crossing rate (indicator of percussiveness)
        zcr = librosa.feature.zero_crossing_rate(y)[0]

        # RMS energy (loudness proxy)
        rms = librosa.feature.rms(y=y)[0]

        # MFCC (timbre characteristics)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

        # Calculate timing precision for context-aware metrics
        timing_precision = self._measure_timing_precision_score(tempo, beats, rms)
        
        # Calculate harmonic coherence for context
        harmonic_coherence_score = self._measure_harmonic_coherence_score(y, sr)
        
        # Advanced spectral analysis (Essentia or enhanced librosa)
        try:
            essentia_features = self.spectral_analyzer.analyze(audio_path)
        except Exception as e:
            logger.warning(f"Advanced spectral analysis failed: {e}")
            essentia_features = {}
        
        # Compute aggregate statistics
        return {
            "duration": float(duration),
            "tempo": float(tempo),
            "key": key,
            "key_name": self._key_to_name(key),
            # Spectral features (mean and std)
            "spectral_centroid_mean": float(np.mean(spectral_centroids)),
            "spectral_centroid_std": float(np.std(spectral_centroids)),
            "spectral_rolloff_mean": float(np.mean(spectral_rolloff)),
            "spectral_rolloff_std": float(np.std(spectral_rolloff)),
            "spectral_bandwidth_mean": float(np.mean(spectral_bandwidth)),
            "spectral_bandwidth_std": float(np.std(spectral_bandwidth)),
            # Energy and dynamics
            "rms_mean": float(np.mean(rms)),
            "rms_std": float(np.std(rms)),
            "loudness": float(librosa.amplitude_to_db(np.mean(rms))),
            # Percussiveness
            "zero_crossing_rate_mean": float(np.mean(zcr)),
            "zero_crossing_rate_std": float(np.std(zcr)),
            # Timbre (MFCC statistics)
            "mfcc_means": [float(x) for x in np.mean(mfccs, axis=1)],
            "mfcc_stds": [float(x) for x in np.std(mfccs, axis=1)],
            # Context-aware derived metrics (considers musicianship!)
            "energy": self._compute_energy(rms),
            "danceability": self._compute_danceability_aware(tempo, beats, timing_precision),
            "valence": self._compute_valence(chroma, spectral_centroids),
            "acousticness": self._compute_acousticness(spectral_rolloff, zcr, rms, spectral_centroids),
            # Raw quality indicators (for transparency)
            "timing_precision_score": float(timing_precision),
            "harmonic_coherence_score": float(harmonic_coherence_score),
            # Advanced spectral features (Essentia or enhanced librosa)
            "essentia_features": essentia_features,
        }

    def detect_hook(
        self, audio_path: str, segment_duration: float = 15.0
    ) -> dict[str, Any]:
        """
        Detect the most "viral" hook segment using energy and novelty.

        Args:
            audio_path: Path to audio file
            segment_duration: Duration of hook segment in seconds

        Returns:
            Dictionary with hook information
        """
        y, sr = self.load_audio(audio_path)
        duration = librosa.get_duration(y=y, sr=sr)

        # Compute onset strength (novelty curve)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)

        # Compute RMS energy
        rms = librosa.feature.rms(y=y, hop_length=512)[0]

        # Normalize both curves
        onset_norm = (onset_env - np.min(onset_env)) / (
            np.max(onset_env) - np.min(onset_env) + 1e-8
        )
        rms_norm = (rms - np.min(rms)) / (np.max(rms) - np.min(rms) + 1e-8)

        # Combine energy and novelty (weighted)
        hook_score = 0.6 * rms_norm + 0.4 * onset_norm[: len(rms_norm)]

        # Convert to time domain
        frames_per_second = sr / 512
        segment_frames = int(segment_duration * frames_per_second)

        # Find best segment using sliding window
        best_score = 0
        best_start_frame = 0

        for i in range(len(hook_score) - segment_frames):
            window_score = np.mean(hook_score[i : i + segment_frames])
            if window_score > best_score:
                best_score = window_score
                best_start_frame = i

        # Convert frames to time
        start_time = best_start_frame / frames_per_second
        end_time = min(start_time + segment_duration, duration)

        # Compute hook score (0-100)
        hook_score_normalized = float(best_score * 100)

        return {
            "start_time": float(start_time),
            "end_time": float(end_time),
            "duration": float(end_time - start_time),
            "hook_score": hook_score_normalized,
            "rationale": self._generate_hook_rationale(hook_score_normalized),
        }

    def _key_to_name(self, key_index: int) -> str:
        """Convert key index to note name."""
        keys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        return keys[key_index % 12]

    def _compute_energy(self, rms: np.ndarray) -> float:
        """Compute energy score (0-1)."""
        # Normalize RMS to 0-1 range
        energy = np.mean(rms)
        return float(np.clip(energy * 10, 0, 1))

    def _measure_timing_precision_score(self, tempo: float, beats: np.ndarray, 
                                          rms: np.ndarray = None) -> float:
        """
        Improved timing precision measurement (0-100 scale).
        
        Now distinguishes intentional syncopation from poor timing.
        Professional syncopated music (hip-hop, electronic) gets proper credit.
        """
        try:
            if len(beats) < 2:
                return 50.0
            
            # Calculate beat intervals
            beat_times = librosa.frames_to_time(beats, sr=self.sample_rate)
            beat_intervals = np.diff(beat_times)
            
            if len(beat_intervals) == 0:
                return 50.0
            
            # Coefficient of variation for beat consistency
            mean_interval = np.mean(beat_intervals)
            std_interval = np.std(beat_intervals)
            
            if mean_interval == 0:
                return 50.0
            
            cv = std_interval / mean_interval
            
            # Check for production quality indicators (professional vs amateur)
            production_quality_boost = 0.0
            
            if rms is not None:
                # Professional production has consistent RMS (compression/mastering)
                rms_cv = np.std(rms) / (np.mean(rms) + 1e-8)
                if rms_cv < 0.5:  # Well-produced, consistent dynamics
                    production_quality_boost = 15.0  # Boost by up to 15 points
                elif rms_cv < 0.7:
                    production_quality_boost = 10.0
            
            # Check for repeating patterns (syncopation vs randomness)
            pattern_consistency = 0.0
            if len(beat_intervals) >= 8:
                # Check if intervals repeat in patterns (syncopation)
                # Compare first half vs second half correlation
                mid_point = len(beat_intervals) // 2
                first_half = beat_intervals[:mid_point]
                second_half = beat_intervals[mid_point:mid_point*2]
                
                if len(first_half) > 0 and len(second_half) > 0 and len(first_half) == len(second_half):
                    correlation = np.corrcoef(first_half, second_half)[0, 1]
                    if not np.isnan(correlation):
                        if correlation > 0.5:  # Strong pattern repetition = intentional
                            pattern_consistency = 10.0
                        elif correlation > 0.3:
                            pattern_consistency = 5.0
            
            # Base score from CV
            if cv < 0.02:
                base_score = 100.0  # Perfect timing (metronome-like, studio quantized)
            elif cv < 0.03:
                base_score = 95.0   # Near-perfect
            elif cv < 0.04:
                base_score = 85.0   # Excellent
            elif cv < 0.05:
                base_score = 75.0   # Very good
            elif cv < 0.06:
                base_score = 65.0   # Acceptable
            elif cv < 0.08:
                base_score = 55.0   # Below average (BUT: see adjustments below)
            elif cv < 0.12:
                base_score = 45.0   # Poor
            elif cv < 0.18:
                base_score = 35.0   # Very poor
            elif cv < 0.25:
                base_score = 25.0   # Terrible
            else:
                base_score = 15.0   # Chaotic
            
            # CRITICAL: Apply adjustments for professional syncopated music
            # If CV is moderate (0.06-0.12) BUT production quality is high,
            # it's likely intentional syncopation, not poor timing
            if 0.06 <= cv <= 0.12:
                adjusted_score = base_score + production_quality_boost + pattern_consistency
            elif cv < 0.06:
                # Good timing, small boost for production quality
                adjusted_score = base_score + production_quality_boost * 0.3
            else:
                # Very poor timing, no boost helps
                adjusted_score = base_score
            
            return float(np.clip(adjusted_score, 0, 100))
                
        except Exception:
            return 50.0
    
    def _measure_harmonic_coherence_score(self, y: np.ndarray, sr: int) -> float:
        """
        Lightweight harmonic coherence measurement (0-100 scale).
        
        Returns just the score for use in context-aware metrics.
        """
        try:
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
            
            # Chord clarity
            chroma_max = np.max(chroma, axis=0)
            chroma_mean = np.mean(chroma, axis=0)
            clarity_ratio = chroma_max / (chroma_mean + 1e-8)
            mean_clarity = np.mean(clarity_ratio)
            
            if mean_clarity > 4.0:
                return 100.0
            elif mean_clarity > 3.0:
                return 85.0
            elif mean_clarity > 2.0:
                return 70.0
            elif mean_clarity > 1.5:
                return 50.0
            else:
                return 30.0
                
        except Exception:
            return 70.0
    
    def _compute_danceability_aware(
        self, tempo: float, beats: np.ndarray, timing_precision: float
    ) -> float:
        """
        Improved danceability score (0-1) with better genre coverage.
        
        NOW CONSIDERS:
        - Multiple danceable tempo ranges (hip-hop, house, pop, etc.)
        - Professional syncopation vs poor timing (via improved timing_precision)
        - Beat strength and regularity
        
        Args:
            tempo: Detected tempo in BPM
            beats: Beat frames
            timing_precision: Timing precision score (0-100, now syncopation-aware)
        
        Returns:
            Danceability score (0-1)
        """
        # IMPROVED: Genre-flexible tempo scoring
        # Different genres have different ideal dance tempos
        tempo_score = 0.0
        
        if 80 <= tempo <= 100:
            # Hip-hop, trap, slow house
            tempo_score = 0.9
        elif 100 <= tempo <= 130:
            # Pop, most hip-hop, house
            tempo_score = 1.0  # Peak danceability range
        elif 130 <= tempo <= 145:
            # Fast house, techno
            tempo_score = 0.85
        elif 70 <= tempo < 80:
            # Slow jams, downtempo
            tempo_score = 0.7
        elif 145 <= tempo <= 160:
            # Drum & bass (half-time), fast techno
            tempo_score = 0.7
        elif 60 <= tempo < 70:
            # Very slow
            tempo_score = 0.5
        elif 160 <= tempo <= 180:
            # Drum & bass, hardcore
            tempo_score = 0.5
        else:
            # Too slow or too fast for most dancing
            tempo_score = 0.3

        # Beat regularity (variance in beat intervals)
        if len(beats) > 1:
            beat_intervals = np.diff(beats)
            beat_regularity = 1.0 - (
                np.std(beat_intervals) / (np.mean(beat_intervals) + 1e-8)
            )
            beat_regularity = max(0, min(1, beat_regularity))
        else:
            beat_regularity = 0.5

        # Timing factor (now properly accounts for intentional syncopation)
        timing_factor = timing_precision / 100.0
        
        # Base danceability (tempo + beat detection)
        base_danceability = 0.5 * tempo_score + 0.5 * beat_regularity
        
        # IMPROVED timing penalty - more aggressive for poor execution
        # Professional music with tight timing or intentional syncopation: 75-85+
        # The Shaggs territory (chaotic, poorly executed): <70
        if timing_precision >= 80:
            # Excellent timing - professional with tight execution
            timing_multiplier = 0.95 + 0.05 * timing_factor  # Minimal penalty
        elif timing_precision >= 70:
            # Good timing - professional but not perfect
            timing_multiplier = 0.75 + 0.20 * timing_factor
        elif timing_precision >= 60:
            # Below average - noticeable timing issues (The Shaggs @ 69.5)
            timing_multiplier = 0.40 + 0.30 * timing_factor
        elif timing_precision >= 50:
            # Poor timing - significant issues
            timing_multiplier = 0.25 + 0.25 * timing_factor
        else:
            # Very poor timing - chaotic/amateur
            timing_multiplier = 0.15 + 0.15 * timing_factor
        
        # Apply penalty
        danceability = base_danceability * timing_multiplier
        
        return float(np.clip(danceability, 0, 1))
    
    def _compute_danceability(
        self, tempo: float, beats: np.ndarray, y: np.ndarray, sr: int
    ) -> float:
        """
        DEPRECATED: Use _compute_danceability_aware instead.
        
        Kept for backwards compatibility.
        """
        # Fallback to basic calculation
        tempo_score = 1.0 - abs(tempo - 110) / 110
        tempo_score = max(0, tempo_score)

        if len(beats) > 1:
            beat_intervals = np.diff(beats)
            beat_regularity = 1.0 - (
                np.std(beat_intervals) / (np.mean(beat_intervals) + 1e-8)
            )
            beat_regularity = max(0, min(1, beat_regularity))
        else:
            beat_regularity = 0.5

        danceability = 0.6 * tempo_score + 0.4 * beat_regularity
        return float(np.clip(danceability, 0, 1))

    def _compute_valence(
        self, chroma: np.ndarray, spectral_centroids: np.ndarray
    ) -> float:
        """
        Compute valence (musical positiveness) score (0-1).

        Higher spectral centroid and major-key tendency → higher valence.
        """
        # Major vs minor tendency (simplified)
        major_profile = np.array([1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1])
        chroma_mean = np.mean(chroma, axis=1)
        major_score = np.dot(chroma_mean, major_profile) / (np.sum(chroma_mean) + 1e-8)

        # Brightness (spectral centroid)
        brightness = np.mean(spectral_centroids) / 4000  # Normalize
        brightness = min(1, brightness)

        # Combine
        valence = 0.6 * major_score + 0.4 * brightness
        return float(np.clip(valence, 0, 1))

    def _compute_acousticness(
        self, spectral_rolloff: np.ndarray, zcr: np.ndarray, rms: np.ndarray = None, 
        spectral_centroid: np.ndarray = None
    ) -> float:
        """
        Compute acousticness score (0-1).
        
        Improved to better distinguish electronic/produced music from acoustic.
        Lower spectral rolloff + natural dynamics → more acoustic.
        Low rolloff + consistent dynamics → electronic/produced (low acousticness).
        """
        mean_rolloff = np.mean(spectral_rolloff)
        mean_zcr = np.mean(zcr)
        
        # Base acousticness from spectral features
        # Lower rolloff = potentially more acoustic
        rolloff_score = 1.0 - (mean_rolloff / 8000)
        rolloff_score = max(0, min(1, rolloff_score))

        # Lower ZCR = potentially more acoustic (less distortion/synthesis)
        zcr_score = 1.0 - mean_zcr
        zcr_score = max(0, min(1, zcr_score))
        
        # CRITICAL: Check for electronic/produced music indicators
        # Electronic music has low rolloff BUT also very consistent dynamics
        electronic_confidence = 0.0
        
        if rms is not None:
            # Electronic/produced music has more consistent loudness
            rms_cv = np.std(rms) / (np.mean(rms) + 1e-8)  # Coefficient of variation
            if rms_cv < 0.4:  # Very consistent = likely electronic/compressed
                electronic_confidence += 0.5
            elif rms_cv < 0.6:
                electronic_confidence += 0.3
        
        if spectral_centroid is not None:
            # Synthesized sounds have more consistent spectral characteristics
            centroid_cv = np.std(spectral_centroid) / (np.mean(spectral_centroid) + 1e-8)
            if centroid_cv < 0.4:  # Very consistent = likely synthesized
                electronic_confidence += 0.3
            elif centroid_cv < 0.6:
                electronic_confidence += 0.2
        
        # High ZCR can also indicate electronic music (digital artifacts)
        if mean_zcr > 0.08:  # Higher than typical acoustic instruments
            electronic_confidence += 0.2
        
        electronic_confidence = min(electronic_confidence, 1.0)
        
        # Compute base acousticness
        base_acousticness = 0.7 * rolloff_score + 0.3 * zcr_score
        
        # If electronic indicators are strong, reduce acousticness significantly
        # Even if spectral rolloff is low
        if electronic_confidence > 0.5:
            # Strong electronic indicators = override rolloff-based score
            acousticness = base_acousticness * (1.0 - electronic_confidence * 0.7)
        else:
            # Weak electronic indicators = trust rolloff-based score more
            acousticness = base_acousticness * (1.0 - electronic_confidence * 0.3)
        
        return float(np.clip(acousticness, 0, 1))

    def extract_quality_metrics(self, audio_path: str) -> dict[str, Any]:
        """
        Extract advanced quality metrics for professional assessment.
        
        Measures:
        - Pitch accuracy (tuning consistency)
        - Timing precision (beat consistency)
        - Harmonic coherence (chord/instrument alignment)
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Dictionary with quality metrics (0-100 scores)
        """
        y, sr = self.load_audio(audio_path)
        
        # 1. Pitch Accuracy (0-100)
        pitch_accuracy = self._measure_pitch_accuracy(y, sr)
        
        # 2. Timing Precision (0-100)
        timing_precision = self._measure_timing_precision(y, sr)
        
        # 3. Harmonic Coherence (0-100)
        harmonic_coherence = self._measure_harmonic_coherence(y, sr)
        
        # Overall quality score (weighted average)
        overall_quality = (
            pitch_accuracy * 0.35 +
            timing_precision * 0.35 +
            harmonic_coherence * 0.30
        )
        
        return {
            "pitch_accuracy": round(pitch_accuracy, 1),
            "timing_precision": round(timing_precision, 1),
            "harmonic_coherence": round(harmonic_coherence, 1),
            "overall_quality": round(overall_quality, 1),
            "quality_grade": self._get_quality_grade(overall_quality),
        }
    
    def _measure_pitch_accuracy(self, y: np.ndarray, sr: int) -> float:
        """
        Measure pitch accuracy/tuning consistency (0-100).
        
        Uses pitch tracking to detect:
        - Pitch stability (low variance = in tune)
        - Pitch confidence (strong fundamental = clear pitch)
        """
        try:
            # Extract pitch using piptrack (faster than pyin)
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr, fmin=80, fmax=400)
            
            # Get pitch trajectory (strongest pitch at each frame)
            pitch_trajectory = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:  # Valid pitch detected
                    pitch_trajectory.append(pitch)
            
            if len(pitch_trajectory) < 10:
                # Not enough pitch data (instrumental or very quiet)
                return 70.0  # Neutral score
            
            pitch_array = np.array(pitch_trajectory)
            
            # 1. Pitch stability (low variance = consistent tuning)
            # Convert to cents (100 cents = 1 semitone)
            pitch_cents = 1200 * np.log2(pitch_array / np.median(pitch_array) + 1e-8)
            pitch_variance = np.std(pitch_cents)
            
            # Score: lower variance = better (professional: <30 cents std)
            if pitch_variance < 30:
                stability_score = 100
            elif pitch_variance < 50:
                stability_score = 80
            elif pitch_variance < 80:
                stability_score = 60
            elif pitch_variance < 120:
                stability_score = 40
            else:
                stability_score = 20  # Very unstable (The Shaggs territory)
            
            # 2. Pitch confidence (strong fundamental detection)
            confidence_score = min(len(pitch_trajectory) / (pitches.shape[1] * 0.8), 1.0) * 100
            
            # Combine scores
            pitch_accuracy = (stability_score * 0.7) + (confidence_score * 0.3)
            return float(np.clip(pitch_accuracy, 0, 100))
            
        except Exception as e:
            logger.warning(f"Pitch accuracy measurement failed: {e}")
            return 70.0  # Neutral score on error
    
    def _measure_timing_precision(self, y: np.ndarray, sr: int) -> float:
        """
        Measure timing precision/beat consistency (0-100).
        
        Detects:
        - Beat regularity (consistent tempo)
        - Onset strength (clear attack points)
        """
        try:
            # Track beats
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            
            if len(beats) < 4:
                return 50.0  # Not enough beats to measure
            
            # 1. Beat interval consistency
            beat_times = librosa.frames_to_time(beats, sr=sr)
            beat_intervals = np.diff(beat_times)
            
            # Coefficient of variation (CV) - lower is better
            mean_interval = np.mean(beat_intervals)
            std_interval = np.std(beat_intervals)
            cv = std_interval / (mean_interval + 1e-8)
            
            # Score: professional recordings have CV < 0.05
            if cv < 0.05:
                consistency_score = 100
            elif cv < 0.10:
                consistency_score = 85
            elif cv < 0.15:
                consistency_score = 70
            elif cv < 0.25:
                consistency_score = 50
            else:
                consistency_score = 30  # Erratic timing (The Shaggs)
            
            # 2. Onset strength (clear rhythmic definition)
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            onset_strength = np.mean(onset_env) / (np.std(onset_env) + 1e-8)
            
            # Normalize to 0-100
            onset_score = min(onset_strength * 20, 100)
            
            # Combine scores
            timing_precision = (consistency_score * 0.7) + (onset_score * 0.3)
            return float(np.clip(timing_precision, 0, 100))
            
        except Exception as e:
            logger.warning(f"Timing precision measurement failed: {e}")
            return 70.0  # Neutral score on error
    
    def _measure_harmonic_coherence(self, y: np.ndarray, sr: int) -> float:
        """
        Measure harmonic coherence (0-100).
        
        Detects:
        - Chord clarity (strong harmonic structure)
        - Tonal consistency (instruments in tune with each other)
        """
        try:
            # Extract chromagram (pitch class distribution)
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
            
            # 1. Chord clarity - how well-defined are the chords?
            # Strong chords have high peak-to-average ratio in chroma
            chroma_max = np.max(chroma, axis=0)
            chroma_mean = np.mean(chroma, axis=0)
            clarity_ratio = chroma_max / (chroma_mean + 1e-8)
            
            # Average clarity across time
            mean_clarity = np.mean(clarity_ratio)
            
            # Score: professional recordings have clarity > 3.0
            if mean_clarity > 4.0:
                clarity_score = 100
            elif mean_clarity > 3.0:
                clarity_score = 85
            elif mean_clarity > 2.0:
                clarity_score = 70
            elif mean_clarity > 1.5:
                clarity_score = 50
            else:
                clarity_score = 30  # Muddy/chaotic harmonics
            
            # 2. Tonal consistency - do the pitch classes stay coherent?
            # Measure variance in chroma distribution over time
            chroma_variance = np.mean(np.std(chroma, axis=1))
            
            # Lower variance = more consistent tonality
            if chroma_variance < 0.10:
                consistency_score = 100
            elif chroma_variance < 0.15:
                consistency_score = 80
            elif chroma_variance < 0.20:
                consistency_score = 60
            else:
                consistency_score = 40  # Inconsistent tonality
            
            # Combine scores
            harmonic_coherence = (clarity_score * 0.6) + (consistency_score * 0.4)
            return float(np.clip(harmonic_coherence, 0, 100))
            
        except Exception as e:
            logger.warning(f"Harmonic coherence measurement failed: {e}")
            return 70.0  # Neutral score on error
    
    def _get_quality_grade(self, score: float) -> str:
        """Convert quality score to grade."""
        if score >= 90:
            return "Professional"
        elif score >= 75:
            return "Advanced"
        elif score >= 60:
            return "Intermediate"
        elif score >= 45:
            return "Developing"
        else:
            return "Amateur"

    def _generate_hook_rationale(self, score: float) -> str:
        """Generate human-readable rationale for hook score."""
        if score >= 80:
            return "Exceptional viral potential - high energy and memorable peak"
        if score >= 65:
            return "Strong hook potential - notable energy and dynamics"
        if score >= 50:
            return "Moderate hook potential - decent energy variation"
        return "Lower hook potential - consider emphasizing dynamics"


# Convenience function
def extract_audio_features(
    audio_path: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    """
    Extract comprehensive audio analysis: sonic genome, hook data, quality metrics, mastering quality, and chord analysis.

    Args:
        audio_path: Path to audio file

    Returns:
        Tuple of (sonic_genome, hook_data, quality_metrics, mastering_quality, chord_analysis)
    """
    from .mastering_analyzer import MasteringAnalyzer
    from .chord_analyzer import ChordAnalyzer
    from .hook_detector_advanced import ViralHookDetector

    extractor = AudioFeatureExtractor()
    sonic_genome = extractor.extract_sonic_genome(audio_path)
    hook_data = extractor.detect_hook(audio_path)
    quality_metrics = extractor.extract_quality_metrics(audio_path)

    # Add mastering quality analysis
    mastering_analyzer = MasteringAnalyzer()
    mastering_quality = mastering_analyzer.analyze(audio_path)

    # Add chord analysis
    chord_analyzer = ChordAnalyzer()
    chord_analysis = chord_analyzer.analyze(audio_path)

    # Add viral segments detection to hook_data
    try:
        viral_detector = ViralHookDetector()
        viral_result = viral_detector.detect_viral_segments(audio_path, segment_duration=15.0, top_n=5)
        if viral_result.get("viral_segments"):
            hook_data["viral_segments"] = viral_result["viral_segments"]
            logger.info(f"✅ Detected {len(viral_result['viral_segments'])} viral segments")
    except Exception as e:
        logger.warning(f"Viral segment detection failed: {e}")
        hook_data["viral_segments"] = []

    return sonic_genome, hook_data, quality_metrics, mastering_quality, chord_analysis

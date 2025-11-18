"""Advanced spectral analysis using Essentia (optional) and enhanced librosa features.

Essentia provides production-grade audio analysis from Music Technology Group (MTG).
Falls back to enhanced librosa analysis if essentia is not available.
"""

import logging
from typing import Any

import librosa
import numpy as np

logger = logging.getLogger(__name__)

# Try to import essentia (optional dependency)
ESSENTIA_AVAILABLE = False
try:
    import essentia
    import essentia.standard as es

    ESSENTIA_AVAILABLE = True
    logger.info("✅ Essentia loaded successfully for advanced spectral analysis")
except ImportError:
    logger.warning(
        "⚠️ Essentia not available - using librosa-only spectral analysis. "
        "Install essentia-tensorflow for enhanced features: pip install essentia-tensorflow"
    )


class AdvancedSpectralAnalyzer:
    """
    Advanced spectral and timbral analysis.

    Uses Essentia when available for production-grade features,
    falls back to enhanced librosa analysis otherwise.
    """

    def __init__(self, sample_rate: int = 22050) -> None:
        """
        Initialize advanced spectral analyzer.

        Args:
            sample_rate: Target sample rate for analysis
        """
        self.sample_rate = sample_rate
        self.use_essentia = ESSENTIA_AVAILABLE

    def analyze(self, audio_path: str) -> dict[str, Any]:
        """
        Perform comprehensive spectral analysis.

        Args:
            audio_path: Path to audio file

        Returns:
            Dictionary with advanced spectral features
        """
        if self.use_essentia:
            return self._analyze_with_essentia(audio_path)
        else:
            return self._analyze_with_librosa(audio_path)

    def _analyze_with_essentia(self, audio_path: str) -> dict[str, Any]:
        """
        Perform analysis using Essentia algorithms.

        Args:
            audio_path: Path to audio file

        Returns:
            Essentia-based spectral features
        """
        try:
            # Load audio with Essentia
            loader = es.MonoLoader(filename=audio_path, sampleRate=self.sample_rate)
            audio = loader()

            # Rhythm features
            rhythm_extractor = es.RhythmExtractor2013()
            bpm, beats, beats_confidence, _, beats_intervals = rhythm_extractor(audio)

            # Tonal features (HPCP - Harmonic Pitch Class Profile)
            spectrum = es.Spectrum()
            spectral_peaks = es.SpectralPeaks()
            hpcp = es.HPCP()

            # Process in frames
            frame_size = 4096
            hop_size = 2048
            hpcp_values = []

            for frame in es.FrameGenerator(
                audio, frameSize=frame_size, hopSize=hop_size
            ):
                spec = spectrum(frame)
                freqs, mags = spectral_peaks(spec)
                hpcp_frame = hpcp(freqs, mags)
                hpcp_values.append(hpcp_frame)

            hpcp_mean = np.mean(hpcp_values, axis=0) if hpcp_values else np.zeros(12)

            # Key detection
            key_extractor = es.KeyExtractor()
            key, scale, strength = key_extractor(audio)

            # Spectral complexity
            spectral_complexity = es.SpectralComplexity()
            complexity_values = []

            for frame in es.FrameGenerator(
                audio, frameSize=frame_size, hopSize=hop_size
            ):
                spec = spectrum(frame)
                complexity = spectral_complexity(spec)
                complexity_values.append(complexity)

            # Inharmonicity
            inharmonicity_extractor = es.Inharmonicity()
            inharmonicity_values = []

            for frame in es.FrameGenerator(
                audio, frameSize=frame_size, hopSize=hop_size
            ):
                spec = spectrum(frame)
                freqs, mags = spectral_peaks(spec)
                if len(freqs) > 0:
                    inharmonicity = inharmonicity_extractor(freqs, mags)
                    inharmonicity_values.append(inharmonicity)

            # Dissonance
            dissonance_extractor = es.Dissonance()
            dissonance_values = []

            for frame in es.FrameGenerator(
                audio, frameSize=frame_size, hopSize=hop_size
            ):
                spec = spectrum(frame)
                freqs, mags = spectral_peaks(spec)
                if len(freqs) > 0:
                    dissonance = dissonance_extractor(freqs, mags)
                    dissonance_values.append(dissonance)

            return {
                "provider": "essentia",
                "rhythm": {
                    "bpm": float(bpm),
                    "beats_count": int(len(beats)),
                    "beats_confidence": float(beats_confidence),
                    "beat_regularity": float(
                        1.0 - np.std(beats_intervals) / (np.mean(beats_intervals) + 1e-6)
                        if len(beats_intervals) > 1
                        else 0.0
                    ),
                },
                "tonal": {
                    "key": key,
                    "scale": scale,
                    "key_strength": float(strength),
                    "hpcp_mean": hpcp_mean.tolist(),
                    "tonal_clarity": float(np.max(hpcp_mean) / (np.mean(hpcp_mean) + 1e-6)),
                },
                "spectral": {
                    "complexity_mean": float(np.mean(complexity_values))
                    if complexity_values
                    else 0.0,
                    "complexity_std": float(np.std(complexity_values))
                    if complexity_values
                    else 0.0,
                    "inharmonicity_mean": float(np.mean(inharmonicity_values))
                    if inharmonicity_values
                    else 0.0,
                    "dissonance_mean": float(np.mean(dissonance_values))
                    if dissonance_values
                    else 0.0,
                    "dissonance_std": float(np.std(dissonance_values))
                    if dissonance_values
                    else 0.0,
                },
            }

        except Exception as e:
            logger.error(f"Essentia analysis failed: {e}, falling back to librosa")
            return self._analyze_with_librosa(audio_path)

    def _analyze_with_librosa(self, audio_path: str) -> dict[str, Any]:
        """
        Enhanced spectral analysis using librosa.

        Args:
            audio_path: Path to audio file

        Returns:
            Librosa-based spectral features
        """
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=self.sample_rate, mono=True)

            # Tempo and beats
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            beat_times = librosa.frames_to_time(beats, sr=sr)
            beat_intervals = np.diff(beat_times) if len(beat_times) > 1 else np.array([])

            # Chroma features (HPCP equivalent)
            chroma_cqt = librosa.feature.chroma_cqt(y=y, sr=sr)
            chroma_mean = np.mean(chroma_cqt, axis=1)

            # Key estimation (simple approach)
            key_index = int(np.argmax(chroma_mean))
            key_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
            estimated_key = key_names[key_index]

            # Spectral features
            spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
            spectral_flatness = librosa.feature.spectral_flatness(y=y)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)

            # Harmonic-percussive separation for complexity estimation
            y_harmonic, y_percussive = librosa.effects.hpss(y)
            harmonic_ratio = np.mean(np.abs(y_harmonic)) / (
                np.mean(np.abs(y)) + 1e-6
            )

            # Zero-crossing rate (inharmonicity proxy)
            zcr = librosa.feature.zero_crossing_rate(y)

            return {
                "provider": "librosa",
                "rhythm": {
                    "bpm": float(tempo),
                    "beats_count": int(len(beats)),
                    "beats_confidence": 0.8,  # Default value (librosa doesn't provide this)
                    "beat_regularity": float(
                        1.0 - np.std(beat_intervals) / (np.mean(beat_intervals) + 1e-6)
                        if len(beat_intervals) > 1
                        else 0.0
                    ),
                },
                "tonal": {
                    "key": estimated_key,
                    "scale": "major",  # Librosa doesn't detect scale
                    "key_strength": float(
                        np.max(chroma_mean) / (np.mean(chroma_mean) + 1e-6)
                    ),
                    "hpcp_mean": chroma_mean.tolist(),
                    "tonal_clarity": float(
                        np.max(chroma_mean) / (np.mean(chroma_mean) + 1e-6)
                    ),
                },
                "spectral": {
                    "complexity_mean": float(np.mean(spectral_contrast)),
                    "complexity_std": float(np.std(spectral_contrast)),
                    "inharmonicity_mean": float(np.mean(zcr)),
                    "dissonance_mean": float(1.0 - harmonic_ratio),
                    "dissonance_std": float(np.std(spectral_flatness)),
                    "spectral_flatness_mean": float(np.mean(spectral_flatness)),
                    "spectral_rolloff_mean": float(np.mean(spectral_rolloff)),
                },
            }

        except Exception as e:
            logger.error(f"Librosa spectral analysis failed: {e}")
            return {
                "provider": "none",
                "error": str(e),
                "rhythm": {},
                "tonal": {},
                "spectral": {},
            }


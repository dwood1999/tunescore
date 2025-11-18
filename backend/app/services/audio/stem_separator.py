"""Stem separation using Demucs for production quality assessment.

Demucs is Meta's state-of-the-art source separation model.
Separates audio into vocals, drums, bass, and other stems.
"""

import logging
import os
from pathlib import Path
from typing import Any

import librosa
import numpy as np
import soundfile as sf

logger = logging.getLogger(__name__)

# Try to import demucs (optional dependency)
DEMUCS_AVAILABLE = False
try:
    from demucs.apply import apply_model
    from demucs.pretrained import get_model
    import torch

    DEMUCS_AVAILABLE = True
    logger.info("✅ Demucs loaded successfully for stem separation")
except ImportError:
    logger.warning(
        "⚠️ Demucs not available - stem separation disabled. "
        "Install with: pip install demucs"
    )


class StemSeparator:
    """
    Separate audio into stems (vocals, drums, bass, other) using Demucs.

    This is an expensive operation (~10-20s per track) and should be called
    only on-demand or for high-value analysis.
    """

    def __init__(self, model_name: str = "htdemucs", device: str = "cpu") -> None:
        """
        Initialize stem separator.

        Args:
            model_name: Demucs model to use ('htdemucs' is recommended)
            device: 'cuda' for GPU or 'cpu'
        """
        self.model_name = model_name
        self.device = device
        self.model = None

        if DEMUCS_AVAILABLE:
            try:
                logger.info(f"Loading Demucs model: {model_name}")
                self.model = get_model(model_name)
                self.model.to(device)
                self.model.eval()
                logger.info(f"✅ Demucs model loaded on {device}")
            except Exception as e:
                logger.error(f"Failed to load Demucs model: {e}")
                self.model = None

    def separate(
        self, audio_path: str, output_dir: str | None = None
    ) -> dict[str, Any]:
        """
        Separate audio into stems and analyze each stem.

        Args:
            audio_path: Path to input audio file
            output_dir: Directory to save stems (optional)

        Returns:
            Dictionary with stem analysis and file paths
        """
        if not DEMUCS_AVAILABLE or self.model is None:
            logger.warning("Demucs not available, skipping stem separation")
            return {
                "available": False,
                "error": "Demucs not installed or model failed to load",
            }

        try:
            # Load audio
            audio, sr = librosa.load(audio_path, sr=44100, mono=False)

            # Ensure stereo (Demucs expects stereo)
            if audio.ndim == 1:
                audio = np.stack([audio, audio])
            elif audio.shape[0] == 1:
                audio = np.concatenate([audio, audio], axis=0)

            # Convert to torch tensor
            audio_tensor = torch.from_numpy(audio).float().unsqueeze(0).to(self.device)

            # Apply model
            with torch.no_grad():
                sources = apply_model(
                    self.model, audio_tensor, device=self.device, split=True, overlap=0.25
                )

            # Demucs returns: [batch, stems, channels, time]
            # stems order: drums, bass, other, vocals
            sources = sources[0].cpu().numpy()  # Remove batch dimension

            stems_dict = {
                "drums": sources[0],
                "bass": sources[1],
                "other": sources[2],
                "vocals": sources[3],
            }

            # Analyze each stem
            stem_analysis = {}
            stem_paths = {}

            for stem_name, stem_audio in stems_dict.items():
                # Analyze stem
                analysis = self._analyze_stem(stem_audio, sr)
                stem_analysis[stem_name] = analysis

                # Save stem if output_dir provided
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)
                    stem_path = os.path.join(output_dir, f"{stem_name}.wav")

                    # Convert to mono for saving (mix stereo channels)
                    stem_mono = np.mean(stem_audio, axis=0)
                    sf.write(stem_path, stem_mono, sr)
                    stem_paths[stem_name] = stem_path
                    logger.info(f"Saved {stem_name} stem to {stem_path}")

            # Calculate production quality metrics from stems
            production_metrics = self._calculate_production_quality(stem_analysis)

            return {
                "available": True,
                "model": self.model_name,
                "device": self.device,
                "stem_features": stem_analysis,
                "stem_paths": stem_paths,
                "production_quality": production_metrics,
            }

        except Exception as e:
            logger.error(f"Stem separation failed: {e}")
            return {
                "available": True,
                "error": str(e),
                "stem_features": {},
            }

    def _analyze_stem(self, stem_audio: np.ndarray, sr: int) -> dict[str, Any]:
        """
        Analyze individual stem.

        Args:
            stem_audio: Stereo stem audio data
            sr: Sample rate

        Returns:
            Stem analysis metrics
        """
        # Convert to mono for analysis
        stem_mono = np.mean(stem_audio, axis=0) if stem_audio.ndim > 1 else stem_audio

        # RMS energy
        rms = librosa.feature.rms(y=stem_mono)[0]
        rms_mean = float(np.mean(rms))
        rms_std = float(np.std(rms))

        # Spectral features
        spectral_centroid = librosa.feature.spectral_centroid(y=stem_mono, sr=sr)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=stem_mono, sr=sr)[0]
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=stem_mono, sr=sr)[0]

        # Zero-crossing rate
        zcr = librosa.feature.zero_crossing_rate(stem_mono)[0]

        # Presence (how much of the mix this stem occupies)
        presence = float(rms_mean / (np.max(rms) + 1e-6))

        return {
            "rms_mean": rms_mean,
            "rms_std": rms_std,
            "presence": presence,
            "spectral_centroid_mean": float(np.mean(spectral_centroid)),
            "spectral_rolloff_mean": float(np.mean(spectral_rolloff)),
            "spectral_bandwidth_mean": float(np.mean(spectral_bandwidth)),
            "zero_crossing_rate_mean": float(np.mean(zcr)),
            "dynamic_range": float(np.max(rms) - np.min(rms)),
        }

    def _calculate_production_quality(
        self, stem_analysis: dict[str, dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Calculate overall production quality from stem analysis.

        Args:
            stem_analysis: Analysis for each stem

        Returns:
            Production quality metrics
        """
        # Vocal clarity (higher spectral centroid = clearer vocals)
        vocal_clarity = 0.0
        if "vocals" in stem_analysis:
            vocal_sc = stem_analysis["vocals"].get("spectral_centroid_mean", 0)
            vocal_clarity = min(1.0, vocal_sc / 3000.0)  # Normalize to 0-1

        # Bass presence (lower spectral rolloff = more bass)
        bass_presence = 0.0
        if "bass" in stem_analysis:
            bass_rolloff = stem_analysis["bass"].get("spectral_rolloff_mean", 10000)
            bass_presence = max(0.0, 1.0 - bass_rolloff / 5000.0)

        # Drum tightness (lower RMS std = tighter drums)
        drum_tightness = 0.0
        if "drums" in stem_analysis:
            drum_std = stem_analysis["drums"].get("rms_std", 0.1)
            drum_tightness = max(0.0, 1.0 - drum_std)

        # Stereo separation quality (based on 'other' channel dynamics)
        stereo_quality = 0.0
        if "other" in stem_analysis:
            other_dr = stem_analysis["other"].get("dynamic_range", 0)
            stereo_quality = min(1.0, other_dr / 0.5)

        # Overall production score (0-100)
        production_score = int(
            (vocal_clarity * 30 + bass_presence * 25 + drum_tightness * 25 + stereo_quality * 20)
        )

        return {
            "vocal_clarity": round(vocal_clarity, 3),
            "bass_presence": round(bass_presence, 3),
            "drum_tightness": round(drum_tightness, 3),
            "stereo_quality": round(stereo_quality, 3),
            "overall_score": production_score,
        }


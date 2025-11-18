"""ML-based genre classification utilities."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Iterable

import librosa
from transformers import pipeline

GENRE_MODEL_ID = "danilotpnta/HuBERT-Genre-Clf"
DEFAULT_SR = 16000
DEFAULT_DURATION = 30.0


@lru_cache(maxsize=1)
def _genre_pipeline():
    """Lazy load the Hugging Face pipeline once."""
    return pipeline("audio-classification", model=GENRE_MODEL_ID)


def classify_audio(audio: np.ndarray, sampling_rate: int, top_k: int = 10) -> list[dict[str, float]]:
    """Classify raw audio array and return Hugging Face results."""
    clf = _genre_pipeline()
    return clf(audio, sampling_rate=sampling_rate, top_k=top_k)


def classify_file(audio_path: str | Path, *, sr: int = DEFAULT_SR, duration: float = DEFAULT_DURATION, top_k: int = 10) -> list[dict[str, float]]:
    """Load an audio file and classify it."""
    audio, sr = librosa.load(str(audio_path), sr=sr, duration=duration)
    return classify_audio(audio, sr, top_k=top_k)


def to_score_map(results: Iterable[dict[str, float]]) -> dict[str, float]:
    """Convert Hugging Face results to a lowercase score map."""
    scores: dict[str, float] = {}
    for item in results:
        label = item.get("label", "").lower()
        score = float(item.get("score", 0.0))
        scores[label] = max(score, scores.get(label, 0.0))
    return scores

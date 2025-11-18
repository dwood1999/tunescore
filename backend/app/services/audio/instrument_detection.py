"""Instrument detection service using MIT AST AudioSet model."""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict, List

from transformers import pipeline


MODEL_ID = "MIT/ast-finetuned-audioset-10-10-0.4593"
TARGET_INSTRUMENTS = {
    "violin": ["violin", "fiddle", "violin, fiddle"],
    "acoustic_guitar": ["acoustic guitar"],
    "electric_guitar": ["electric guitar"],
    "drums": ["drum", "drum kit", "snare drum", "bass drum"],
    "harmonica": ["harmonica"],
    "banjo": ["banjo"],
}


@lru_cache(maxsize=1)
def _load_pipeline():
    return pipeline("audio-classification", model=MODEL_ID)


def detect_instruments(audio: Any, sampling_rate: int, top_k: int = 100) -> Dict[str, float]:
    """Detect instruments from raw audio array."""
    clf = _load_pipeline()
    results: List[Dict[str, Any]] = clf(audio, sampling_rate=sampling_rate, top_k=top_k)
    scored = {item["label"].lower(): float(item["score"]) for item in results}

    instrument_scores: Dict[str, float] = {}
    for instrument, keywords in TARGET_INSTRUMENTS.items():
        score = max((scored.get(keyword, 0.0) for keyword in keywords), default=0.0)
        instrument_scores[instrument] = score

    # keep top generic labels for debugging
    return {
        "raw": scored,
        "instruments": instrument_scores,
    }

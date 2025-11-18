#!/usr/bin/env python3
"""Demo: combine ML genre prediction with instrument detection."""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

import numpy as np


def main() -> None:
    print("=" * 70)
    print("Genre + Instrument Ensemble Demo")
    print("=" * 70)

    try:
        from transformers import pipeline
    except ImportError:
        print("❌ transformers missing. Run poetry add transformers torch torchaudio")
        return

    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from app.services.audio.instrument_detection import detect_instruments

    model_id = "danilotpnta/HuBERT-Genre-Clf"
    print("\n📥 Loading genre classifier (HuBERT)...")
    classifier = pipeline("audio-classification", model=model_id)
    print("✓ Genre classifier ready")

    audio_path = Path("/home/dwood/tunescore/backend/files/1/11/audio.mp3")
    if not audio_path.exists():
        print(f"⚠️ Audio file missing: {audio_path}")
        return

    try:
        import librosa
    except ImportError:
        print("❌ librosa missing")
        return

    audio, sr = librosa.load(str(audio_path), sr=16000, duration=30)
    print(f"\n🎵 Loaded audio: {len(audio)/sr:.1f}s at {sr}Hz")

    print("\n⏳ ML genre prediction...")
    ml_results = classifier(audio, sampling_rate=sr, top_k=10)
    ml_scores = {item["label"].lower(): float(item["score"]) for item in ml_results}

    print("\n⏳ Instrument detection...")
    instrument_result = detect_instruments(audio, sr)
    instrument_scores = instrument_result["instruments"]

    # Apply heuristic boosts based on detected instruments
    boosts = defaultdict(float)
    violin_score = instrument_scores.get("violin", 0.0)
    if violin_score > 0.01:
        boosts["country"] += 4.0 * violin_score
        boosts["bluegrass"] += 3.0 * violin_score
        boosts["folk"] += 1.5 * violin_score

    acoustic_score = instrument_scores.get("acoustic_guitar", 0.0)
    if acoustic_score > 0.005:
        boosts["country"] += 1.5 * acoustic_score
        boosts["folk"] += 0.8 * acoustic_score

    harmonica_score = instrument_scores.get("harmonica", 0.0)
    if harmonica_score > 0.003:
        boosts["country"] += 1.0 * harmonica_score
        boosts["blues"] += 0.7 * harmonica_score

    drum_score = instrument_scores.get("drums", 0.0)
    if drum_score > 0.005:
        boosts["rock"] += 0.4 * drum_score

    # Combine scores
    final_scores = defaultdict(float)
    all_genres = set(list(ml_scores.keys()) + list(boosts.keys()))
    for genre in all_genres:
        final_scores[genre] = ml_scores.get(genre, 0.0) * 0.2 + boosts.get(genre, 0.0)

    # Normalize
    total = sum(final_scores.values()) or 1.0
    normalized = {genre: score / total for genre, score in final_scores.items()}

    print("\n" + "=" * 70)
    print("ML MODEL ONLY")
    print("=" * 70)
    for item in ml_results[:5]:
        print(f"{item['label']:10s} {item['score']*100:6.2f}%")

    print("\n" + "=" * 70)
    print("INSTRUMENT SCORES")
    print("=" * 70)
    for name, score in instrument_scores.items():
        print(f"{name:15s}: {score*100:6.2f}%")

    print("\n" + "=" * 70)
    print("ENSEMBLE RESULT")
    print("=" * 70)
    for genre, score in sorted(normalized.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"{genre:10s} {score*100:6.2f}%")

    top_genre = max(normalized.items(), key=lambda x: x[1])
    print(f"\n🎯 Final predicted genre: {top_genre[0].title()} ({top_genre[1]*100:.2f}%)")


if __name__ == "__main__":
    main()

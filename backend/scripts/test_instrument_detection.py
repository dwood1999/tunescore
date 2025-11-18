#!/usr/bin/env python3
"""Test instrument detection with MIT AST model."""

import sys
from pathlib import Path


def main() -> None:
    print("=" * 70)
    print("MIT AST Instrument Detection Test")
    print("=" * 70)

    try:
        from transformers import pipeline
    except ImportError:
        print("\n❌ transformers not installed. Run poetry add transformers torch torchaudio")
        return

    model_id = "MIT/ast-finetuned-audioset-10-10-0.4593"
    print("\n📥 Loading instrument detection model ...")
    print(f"   Model: {model_id}")
    print("   Task: Audio tagging (527 AudioSet classes)")

    try:
        classifier = pipeline(
            "audio-classification",
            model=model_id,
        )
        print("✓ Model loaded successfully!")
    except Exception as exc:
        print(f"❌ Failed to load model: {exc}")
        return

    audio_path = Path("/home/dwood/tunescore/backend/files/1/11/audio.mp3")
    if not audio_path.exists():
        print(f"\n⚠️ Audio file not found: {audio_path}")
        return

    try:
        import librosa
    except ImportError:
        print("\n❌ librosa not installed (should already be in deps).")
        return

    print(f"\n🎵 Analyzing: {audio_path}")
    audio, sr = librosa.load(str(audio_path), sr=16000, duration=30)
    print(f"   Loaded {len(audio) / sr:.1f}s audio at {sr}Hz")

    print("\n⏳ Running instrument detection (top 10 tags)...")
    results = classifier(audio, sampling_rate=sr, top_k=10)

    print("\n" + "=" * 70)
    print("INSTRUMENT DETECTION RESULTS")
    print("=" * 70)
    for rank, item in enumerate(results, start=1):
        label = item["label"].replace("_", " ")
        score = item["score"] * 100
        bar = "█" * int(score / 2)
        print(f"{rank:2d}. {label:25s} {score:6.2f}% {bar}")

    print("\nDone.")


if __name__ == "__main__":
    sys.exit(main())

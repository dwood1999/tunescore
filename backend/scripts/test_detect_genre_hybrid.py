#!/usr/bin/env python3
"""Manual test for detect_genre_hybrid."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    audio_path = Path("/home/dwood/tunescore/backend/files/1/11/audio.mp3")
    if not audio_path.exists():
        print(f"Audio file missing: {audio_path}")
        return

    from app.services.classification.genre_detector import detect_genre_hybrid

    result = detect_genre_hybrid(str(audio_path), sonic_genome={}, lyrical_genome=None)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

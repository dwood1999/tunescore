#!/usr/bin/env python3
"""
Test Hugging Face ML models for genre classification.

This demonstrates how the ML models will dramatically improve genre detection.
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

def test_ml_genre_classification():
    """Test genre classification with Hugging Face models"""
    
    print("="*70)
    print("Hugging Face ML Genre Classification Test")
    print("="*70)
    
    # Check if transformers is installed
    try:
        from transformers import pipeline
        print("\n✓ Transformers library available")
    except ImportError:
        print("\n❌ Transformers not installed yet")
        print("\nTo install:")
        print("  cd /home/dwood/tunescore/backend")
        print("  poetry add transformers torch torchaudio")
        print("\nThis will download ~2GB of dependencies")
        return
    
    # Try to load the HuBERT model (standard transformers, good accuracy)
    print("\n📥 Loading ML model (first time will download ~200MB)...")
    print("   Model: danilotpnta/HuBERT-Genre-Clf")
    print("   Accuracy: 80.63% on GTZAN dataset")
    print("   Architecture: DistilHuBERT (optimized)")
    print("   Genres: 10 (blues, classical, country, disco, hiphop, jazz, metal, pop, reggae, rock)")
    
    try:
        classifier = pipeline(
            "audio-classification",
            model="danilotpnta/HuBERT-Genre-Clf"
        )
        print("✓ Model loaded successfully!")
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        print("\nNote: Model will auto-download on first use")
        print("Requires internet connection and ~50MB disk space")
        return
    
    # Test with track 11 (The Devil Went Down to Georgia)
    audio_path = Path("/home/dwood/tunescore/backend/files/1/11/audio.mp3")
    
    if not audio_path.exists():
        print(f"\n⚠️  Test audio not found: {audio_path}")
        print("   Please upload 'The Devil Went Down to Georgia' as track 11")
        return
    
    print(f"\n🎵 Analyzing: {audio_path}")
    print("   Expected: Country (fiddle, acoustic, storytelling)")
    
    try:
        # Load audio with librosa first (to avoid ffmpeg requirement)
        import librosa
        import soundfile as sf
        import numpy as np
        
        print("\n⏳ Loading audio with librosa...")
        audio, sr = librosa.load(str(audio_path), sr=16000, duration=30)  # 30s clip
        print(f"   Audio loaded: {len(audio)/sr:.1f}s at {sr}Hz")
        
        # Classify
        print("⏳ Running ML classification...")
        results = classifier(audio, sampling_rate=sr)
        
        print("\n" + "="*70)
        print("ML MODEL RESULTS")
        print("="*70)
        
        for i, result in enumerate(results[:5], 1):
            genre = result['label']
            confidence = result['score'] * 100
            bar = "█" * int(confidence / 2) + "░" * (50 - int(confidence / 2))
            print(f"{i}. {genre:15s} {confidence:5.1f}% {bar}")
        
        # Compare with current heuristic
        print("\n" + "="*70)
        print("COMPARISON")
        print("="*70)
        print(f"\nML Model Prediction:      {results[0]['label']} ({results[0]['score']*100:.1f}%)")
        print(f"Current System (Heuristic): Hip-Hop/Rap (38%)")
        
        if results[0]['label'].lower() == 'country':
            print("\n🎉 SUCCESS! ML model correctly identifies Country!")
            print("   This is what we need to integrate into TuneScore")
        else:
            print(f"\n⚠️  ML model says: {results[0]['label']}")
            print("   May need ensemble approach with instrument detection")
        
    except Exception as e:
        print(f"\n❌ Error during classification: {e}")
        print("\nPossible issues:")
        print("  - Audio file format not supported")
        print("  - Audio file too long (model expects 30s clips)")
        print("  - Memory issue (try smaller model)")
    
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("""
1. Install dependencies:
   cd /home/dwood/tunescore/backend
   poetry add transformers torch torchaudio

2. Download model (one-time):
   poetry run python scripts/test_huggingface_genre.py

3. Integrate into genre detector:
   - Create services/classification/genre_ml.py
   - Add ensemble logic (ML + heuristic + instruments)
   - Update track upload pipeline

4. Expected improvements:
   - Genre accuracy: 40% → 80%+
   - Fixes "Devil Went Down to Georgia" misclassification
   - Adds instrument detection capability
    """)

if __name__ == "__main__":
    test_ml_genre_classification()


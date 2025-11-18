#!/usr/bin/env python3
"""Test script for competitive integration features."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.audio.spectral_advanced import AdvancedSpectralAnalyzer
from app.services.audio.stem_separator import StemSeparator
from app.services.audio.hook_detector_advanced import ViralHookDetector
from app.services.lyrics.multilingual_analyzer import MultilingualAnalyzer
from app.services.lyrics.theme_extractor import ThemeExtractor
from app.services.ai_tagging.mood_classifier import MoodClassifier
from app.services.ai_tagging.pitch_generator import PitchGenerator


def test_spectral_analyzer():
    """Test advanced spectral analysis."""
    print("\n=== Testing Advanced Spectral Analyzer ===")
    analyzer = AdvancedSpectralAnalyzer()
    print(f"✓ Analyzer initialized (using {'essentia' if analyzer.use_essentia else 'librosa'})")
    
    # Test with a sample file if available
    sample_file = "files/1/2/audio.mp3"
    if os.path.exists(sample_file):
        try:
            result = analyzer.analyze(sample_file)
            print(f"✓ Analysis completed: {result.get('provider', 'unknown')} provider")
            print(f"  - Rhythm features: {len(result.get('rhythm', {}))} metrics")
            print(f"  - Tonal features: {len(result.get('tonal', {}))} metrics")
            print(f"  - Spectral features: {len(result.get('spectral', {}))} metrics")
        except Exception as e:
            print(f"✗ Analysis failed: {e}")
    else:
        print(f"⚠ Sample file not found: {sample_file}")


def test_stem_separator():
    """Test stem separation."""
    print("\n=== Testing Stem Separator ===")
    separator = StemSeparator()
    
    if separator.model is None:
        print("⚠ Demucs not available (expected on first run)")
    else:
        print(f"✓ Demucs model loaded: {separator.model_name}")


def test_hook_detector():
    """Test viral hook detection."""
    print("\n=== Testing Viral Hook Detector ===")
    detector = ViralHookDetector()
    print(f"✓ Detector initialized (using {'madmom' if detector.use_madmom else 'librosa'})")
    
    sample_file = "files/1/2/audio.mp3"
    if os.path.exists(sample_file):
        try:
            result = detector.detect_viral_segments(sample_file, segment_duration=15.0, top_n=3)
            print(f"✓ Detection completed: {result.get('provider', 'unknown')} provider")
            print(f"  - Total segments analyzed: {result.get('total_segments_analyzed', 0)}")
            print(f"  - Viral segments found: {len(result.get('viral_segments', []))}")
            
            if result.get('viral_segments'):
                top_segment = result['viral_segments'][0]
                print(f"  - Top segment: {top_segment['start_time']}-{top_segment['end_time']}s (score: {top_segment['score']})")
        except Exception as e:
            print(f"✗ Detection failed: {e}")


def test_multilingual_analyzer():
    """Test multilingual analysis."""
    print("\n=== Testing Multilingual Analyzer ===")
    analyzer = MultilingualAnalyzer()
    print(f"✓ Analyzer initialized")
    print(f"  - Language detection: {'✓' if analyzer.has_langdetect else '✗'}")
    print(f"  - Translation: {'✓' if analyzer.has_translator else '✗'}")
    print(f"  - NER (spaCy): {'✓' if analyzer.has_spacy else '✗'}")
    
    # Test with English text
    test_lyrics = "I love you more than words can say. You're my sunshine on a rainy day."
    result = analyzer.analyze(test_lyrics)
    print(f"\nEnglish text analysis:")
    print(f"  - Language: {result.get('language', 'unknown')}")
    print(f"  - Entities: {len(result.get('entities', []))}")
    
    # Test with Spanish text
    spanish_lyrics = "Te amo más de lo que las palabras pueden decir. Eres mi sol en un día lluvioso."
    result = analyzer.analyze(spanish_lyrics)
    print(f"\nSpanish text analysis:")
    print(f"  - Language: {result.get('language', 'unknown')}")
    print(f"  - Translated: {result.get('was_translated', False)}")


def test_theme_extractor():
    """Test theme extraction."""
    print("\n=== Testing Theme Extractor ===")
    extractor = ThemeExtractor()
    
    if extractor.classifier is None:
        print("⚠ Zero-shot model not loaded (may need to download)")
    else:
        print(f"✓ Model loaded: {extractor.model_name}")
        
        # Test with sample lyrics
        test_lyrics = "I'm feeling lost and alone, searching for a way back home. The memories haunt me every night."
        try:
            result = extractor.extract_themes(test_lyrics, top_n=3, threshold=0.3)
            print(f"✓ Themes extracted: {len(result.get('themes', {}))} themes")
            for theme, score in result.get('themes', {}).items():
                print(f"  - {theme}: {score}")
        except Exception as e:
            print(f"✗ Extraction failed: {e}")


def test_mood_classifier():
    """Test mood classification."""
    print("\n=== Testing Mood Classifier ===")
    classifier = MoodClassifier()
    print("✓ Classifier initialized")
    
    # Test with sample features
    sonic_genome = {
        "energy": 0.8,
        "valence": 0.7,
        "tempo": 128,
        "acousticness": 0.3,
        "speechiness": 0.1,
        "timing_precision_score": 0.85,
    }
    
    lyrical_genome = {
        "sentiment": {"compound": 0.6}
    }
    
    result = classifier.classify(sonic_genome, lyrical_genome)
    print(f"✓ Mood classification complete")
    print(f"  - Primary mood: {result.get('primary_mood', 'unknown')}")
    print(f"  - All moods: {', '.join(result.get('moods', []))}")
    print(f"  - Energy level: {result.get('energy_level', 'unknown')}")
    print(f"  - Valence level: {result.get('valence_level', 'unknown')}")
    
    # Test commercial tags
    tags = classifier.classify_commercial_tags(sonic_genome)
    print(f"  - Commercial tags: {', '.join(tags)}")


def test_pitch_generator():
    """Test pitch generation."""
    print("\n=== Testing Pitch Generator ===")
    
    # Check if API key is available
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠ ANTHROPIC_API_KEY not set - skipping pitch generation test")
        return
    
    try:
        generator = PitchGenerator()
        print("✓ Generator initialized with Claude API")
        
        # Test with mock data
        sonic_genome = {
            "tempo": 125,
            "energy": 0.75,
            "valence": 0.65,
            "genre": "indie-pop",
        }
        
        tags = {
            "moods": ["uplifting", "energetic"],
            "commercial_tags": ["radio-friendly", "playlist-worthy"],
            "sounds_like": ["The 1975", "LANY"],
        }
        
        # Note: This will cost ~$0.02-0.05
        print("⚠ Generating pitch (will incur API cost ~$0.02-0.05)...")
        result = generator.generate_pitch(
            "Sunset Dreams",
            "indie Artist",
            sonic_genome,
            None,
            tags
        )
        
        if "error" not in result:
            print(f"✓ Pitch generated (cost: ${result.get('cost', 0):.4f})")
            print(f"  - Elevator pitch: {result.get('elevator_pitch', '')[:80]}...")
            print(f"  - Tokens used: {result.get('tokens', {}).get('total', 0)}")
        else:
            print(f"✗ Generation failed: {result.get('error', 'unknown')}")
            
    except ValueError as e:
        print(f"⚠ {e}")
    except Exception as e:
        print(f"✗ Generator failed: {e}")


def test_models():
    """Test database models can be imported."""
    print("\n=== Testing Database Models ===")
    try:
        from app.models.track import (
            ArtistMetricsSnapshot,
            PlaylistAppearance,
            BreakoutPrediction,
            ViralAlert,
            TrackTags,
            PitchCopy,
            TrackCredit,
            CollaboratorProfile,
            ArtistCatalogValuation,
        )
        print("✓ All new models imported successfully")
        
        # Check table names
        models = [
            ArtistMetricsSnapshot,
            PlaylistAppearance,
            BreakoutPrediction,
            ViralAlert,
            TrackTags,
            PitchCopy,
            TrackCredit,
            CollaboratorProfile,
            ArtistCatalogValuation,
        ]
        print(f"  - {len(models)} new models defined")
        for model in models:
            print(f"    • {model.__tablename__}")
            
    except ImportError as e:
        print(f"✗ Model import failed: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("TuneScore Competitive Features Test Suite")
    print("=" * 60)
    
    test_models()
    test_spectral_analyzer()
    test_stem_separator()
    test_hook_detector()
    test_multilingual_analyzer()
    test_theme_extractor()
    test_mood_classifier()
    test_pitch_generator()
    
    print("\n" + "=" * 60)
    print("Test Suite Complete")
    print("=" * 60)


#!/usr/bin/env python3
"""Test pitch generation with actual API."""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.ai_tagging.pitch_generator import PitchGenerator

def test_pitch_generation():
    """Test actual pitch generation."""
    print("=== Testing Pitch Generation with Claude API ===\n")
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY not found in environment")
        return
    
    print("✓ API key found\n")
    
    try:
        generator = PitchGenerator()
        print("✓ Generator initialized\n")
        
        # Test data
        sonic_genome = {
            "tempo": 128,
            "energy": 0.85,
            "valence": 0.72,
            "genre": "indie-pop",
            "danceability": 0.68,
        }
        
        lyrical_genome = {
            "themes_advanced": {"love": 0.8, "nostalgia": 0.6},
        }
        
        tags = {
            "moods": ["uplifting", "energetic", "nostalgic"],
            "commercial_tags": ["radio-friendly", "playlist-worthy"],
            "sounds_like": ["The 1975", "LANY"],
        }
        
        print("Generating pitch (this will cost ~$0.02-0.04)...\n")
        
        result = generator.generate_pitch(
            track_title="Sunset Dreams",
            artist_name="Indie Artist",
            sonic_genome=sonic_genome,
            lyrical_genome=lyrical_genome,
            tags=tags
        )
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return
        
        print("✓ Pitch generated successfully!\n")
        print("=" * 60)
        print("ELEVATOR PITCH:")
        print("=" * 60)
        print(result.get("elevator_pitch", "N/A"))
        print("\n" + "=" * 60)
        print("EPK DESCRIPTION:")
        print("=" * 60)
        print(result.get("short_description", "N/A"))
        print("\n" + "=" * 60)
        print("SYNC LICENSING PITCH:")
        print("=" * 60)
        print(result.get("sync_pitch", "N/A"))
        print("\n" + "=" * 60)
        print(f"Cost: ${result.get('cost', 0):.4f}")
        print(f"Tokens: {result.get('tokens', {}).get('total', 0)}")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pitch_generation()


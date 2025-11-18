#!/usr/bin/env python3
"""
Test chord analysis feature.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.audio.chord_analyzer import ChordAnalyzer

print("=" * 60)
print("CHORD PROGRESSION ANALYSIS - TEST")
print("=" * 60)
print()

# Test on first available audio file
files_dir = "/home/dwood/tunescore/backend/files"
audio_file = None

for root, dirs, files in os.walk(files_dir):
    for file in files:
        if file.endswith(('.mp3', '.wav', '.flac')):
            audio_file = os.path.join(root, file)
            break
    if audio_file:
        break

if not audio_file:
    print("❌ No audio files found")
    sys.exit(1)

print(f"Testing on: {audio_file}")
print()

# Analyze chords
analyzer = ChordAnalyzer()

try:
    result = analyzer.analyze(audio_file)
    
    print("✅ CHORD ANALYSIS COMPLETE")
    print()
    print(f"Key: {result['key']}")
    print(f"Unique Chords: {result['unique_chords']}")
    print(f"Progression: {result['progression_name']}")
    print(f"  {result['progression_description']}")
    print()
    print(f"Harmonic Complexity: {result['harmonic_complexity']}/100")
    print(f"Familiarity Score: {result['familiarity_score']}/100")
    print(f"Novelty Score: {result['novelty_score']}/100")
    print()
    
    print("First 10 Chords:")
    for i, chord in enumerate(result['chords'][:10], 1):
        print(f"  {i}. {chord['time']}s: {chord['chord']} (confidence: {chord['confidence']})")
    
    if result['modulations']:
        print()
        print("Key Changes:")
        for mod in result['modulations']:
            print(f"  {mod['time']}s: {mod['from_key']} → {mod['to_key']}")
    
    if result['recommendations']:
        print()
        print("Recommendations:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"  {i}. {rec}")
    
    print()
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()


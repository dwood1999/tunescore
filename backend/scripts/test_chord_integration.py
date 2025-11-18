#!/usr/bin/env python3
"""
Test chord analysis integration with existing track.
"""

import sys
import os
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.track import Track, TrackAsset, Analysis
from app.services.audio.chord_analyzer import ChordAnalyzer


async def test_chord_integration():
    """Test chord analysis integration on an existing track."""
    print("=" * 60)
    print("TESTING CHORD ANALYSIS INTEGRATION")
    print("=" * 60)
    print()

    async with AsyncSessionLocal() as db:
        # Get first track with audio
        stmt = (
            select(Track, TrackAsset, Analysis)
            .join(TrackAsset, Track.id == TrackAsset.track_id)
            .join(Analysis, Track.id == Analysis.track_id)
            .where(TrackAsset.audio_path.isnot(None))
            .limit(1)
        )
        result = await db.execute(stmt)
        row = result.first()

        if not row:
            print("❌ No tracks found with audio")
            return

        track, track_asset, analysis = row

        print(f"Track: {track.title}")
        print(f"Audio: {track_asset.audio_path}")
        print()

        # Analyze chords
        print("Analyzing chord progression...")
        analyzer = ChordAnalyzer()
        
        try:
            chord_analysis = analyzer.analyze(track_asset.audio_path)
            
            print()
            print("✅ CHORD ANALYSIS COMPLETE")
            print()
            print(f"Key: {chord_analysis['key']}")
            print(f"Unique Chords: {chord_analysis['unique_chords']}")
            print(f"Progression: {chord_analysis['progression_name']}")
            print(f"Harmonic Complexity: {chord_analysis['harmonic_complexity']}/100")
            print(f"Familiarity: {chord_analysis['familiarity_score']}/100")
            print(f"Novelty: {chord_analysis['novelty_score']}/100")
            
            if chord_analysis['modulations']:
                print()
                print("Key Changes:")
                for mod in chord_analysis['modulations']:
                    print(f"  {mod['time']}s: {mod['from_key']} → {mod['to_key']}")
            
            if chord_analysis['recommendations']:
                print()
                print("Recommendations:")
                for i, rec in enumerate(chord_analysis['recommendations'], 1):
                    print(f"  {i}. {rec}")
            
            # Update analysis record
            print()
            print("Updating database...")
            analysis.chord_analysis = chord_analysis
            await db.commit()
            print("✅ Database updated")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

    print()
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_chord_integration())


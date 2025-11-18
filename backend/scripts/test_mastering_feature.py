#!/usr/bin/env python3
"""
Test mastering quality feature on existing track.
"""

import sys
import os
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import select
from app.core.database import get_db, AsyncSessionLocal
from app.models.track import Track, TrackAsset, Analysis
from app.services.audio.mastering_analyzer import MasteringAnalyzer


async def test_mastering_quality():
    """Test mastering quality analysis on an existing track."""
    print("=" * 60)
    print("TESTING MASTERING QUALITY FEATURE")
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

        # Analyze mastering quality
        print("Analyzing mastering quality...")
        analyzer = MasteringAnalyzer()
        
        try:
            mastering_quality = analyzer.analyze(track_asset.audio_path)
            
            print()
            print("✅ MASTERING QUALITY ANALYSIS COMPLETE")
            print()
            print(f"LUFS: {mastering_quality['lufs']} ({mastering_quality['lufs_grade']})")
            print(f"Peak: {mastering_quality['peak_db']} dBFS")
            print(f"RMS: {mastering_quality['rms_db']} dBFS")
            print(f"Dynamic Range: {mastering_quality['dynamic_range']} DR ({mastering_quality['dr_grade']})")
            print(f"Overall Quality: {mastering_quality['overall_quality']}/100 ({mastering_quality['quality_grade']})")
            print()
            print("Platform Targets:")
            for platform, data in mastering_quality['platform_targets'].items():
                status_emoji = "✅" if data['status'] == 'optimal' else "⚠️"
                print(f"  {status_emoji} {platform.replace('_', ' ').title()}: {data['delta']:+.1f} dB ({data['status']})")
            
            if mastering_quality['recommendations']:
                print()
                print("Recommendations:")
                for i, rec in enumerate(mastering_quality['recommendations'], 1):
                    print(f"  {i}. {rec}")
            
            # Update analysis record
            print()
            print("Updating database...")
            analysis.mastering_quality = mastering_quality
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
    asyncio.run(test_mastering_quality())


#!/usr/bin/env python3
"""Generate viral segments for an existing track."""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models import Track, TrackAsset, Analysis
from app.services.audio.hook_detector_advanced import ViralHookDetector


async def generate_viral_segments(track_id: int):
    """Generate viral segments for a track and update analysis."""
    async with AsyncSessionLocal() as db:
        # Get track and asset
        result = await db.execute(
            select(Track, TrackAsset).join(TrackAsset, Track.id == TrackAsset.track_id).where(Track.id == track_id)
        )
        row = result.first()
        
        if not row:
            print(f"❌ Track {track_id} not found")
            return
        
        track, asset = row
        
        if not asset.audio_path or not Path(asset.audio_path).exists():
            print(f"❌ Audio file not found for track {track_id}: {asset.audio_path}")
            return
        
        # Get latest analysis
        result = await db.execute(
            select(Analysis).where(Analysis.track_id == track_id).order_by(Analysis.created_at.desc())
        )
        analysis = result.scalar_one_or_none()
        
        if not analysis:
            print(f"❌ No analysis found for track {track_id}")
            return
        
        # Generate viral segments
        print(f"🎵 Generating viral segments for track {track_id}...")
        try:
            detector = ViralHookDetector()
            viral_result = detector.detect_viral_segments(
                asset.audio_path, 
                segment_duration=15.0, 
                top_n=5
            )
            
            if viral_result.get("viral_segments"):
                # Update hook_data
                hook_data = dict(analysis.hook_data) if analysis.hook_data else {}
                hook_data["viral_segments"] = viral_result["viral_segments"]
                analysis.hook_data = hook_data
                
                await db.commit()
                await db.refresh(analysis)
                print(f"✅ Generated {len(viral_result['viral_segments'])} viral segments")
                for i, seg in enumerate(viral_result["viral_segments"], 1):
                    print(f"   {i}. {seg['start_time']:.1f}s - {seg['end_time']:.1f}s (score: {seg['score']:.1f})")
            else:
                print("⚠️ No viral segments detected")
        except Exception as e:
            print(f"❌ Error generating viral segments: {e}")
            import traceback
            traceback.print_exc()


async def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_viral_segments_for_track.py <track_id>")
        sys.exit(1)
    
    track_id = int(sys.argv[1])
    await generate_viral_segments(track_id)


if __name__ == "__main__":
    asyncio.run(main())


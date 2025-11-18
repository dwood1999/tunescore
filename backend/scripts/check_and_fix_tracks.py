#!/usr/bin/env python3
"""Check all tracks and generate missing data."""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
from dotenv import load_dotenv
root_env = Path(__file__).parent.parent.parent / ".env"
load_dotenv(root_env)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models import Track, TrackTags, PitchCopy, Analysis, TrackAsset, Artist
from app.services.audio.hook_detector_advanced import ViralHookDetector
from app.services.ai_tagging.mood_classifier import MoodClassifier
from app.services.ai_tagging.pitch_generator import PitchGenerator
from app.services.lyrics.ai_critic import AILyricCritic


async def check_track_data(track_id: int, db: AsyncSession) -> dict:
    """Check what data a track has."""
    result = await db.execute(
        select(Track).where(Track.id == track_id)
    )
    track = result.scalar_one_or_none()
    
    if not track:
        return None
    
    # Check TrackTags
    tags_result = await db.execute(
        select(TrackTags).where(TrackTags.track_id == track_id)
    )
    has_tags = tags_result.scalar_one_or_none() is not None
    
    # Check PitchCopy
    pitch_result = await db.execute(
        select(PitchCopy).where(PitchCopy.track_id == track_id)
    )
    has_pitch = pitch_result.scalar_one_or_none() is not None
    
    # Check Analysis
    analysis_result = await db.execute(
        select(Analysis).where(Analysis.track_id == track_id).order_by(Analysis.created_at.desc())
    )
    analysis = analysis_result.scalar_one_or_none()
    
    has_viral = False
    has_lyric_critique = False
    has_analysis = analysis is not None
    
    if analysis:
        hook_data = analysis.hook_data or {}
        has_viral = bool(hook_data.get('viral_segments'))
        has_lyric_critique = bool(analysis.ai_lyric_critique)
    
    # Check TrackAsset
    asset_result = await db.execute(
        select(TrackAsset).where(TrackAsset.track_id == track_id)
    )
    asset = asset_result.scalar_one_or_none()
    has_audio = asset is not None and asset.audio_path and Path(asset.audio_path).exists()
    
    return {
        'track': track,
        'asset': asset,
        'analysis': analysis,
        'has_tags': has_tags,
        'has_pitch': has_pitch,
        'has_viral': has_viral,
        'has_lyric_critique': has_lyric_critique,
        'has_analysis': has_analysis,
        'has_audio': has_audio,
    }


async def generate_missing_data(track_id: int):
    """Generate missing data for a track."""
    async with AsyncSessionLocal() as db:
        data = await check_track_data(track_id, db)
        
        if not data:
            print(f"❌ Track {track_id} not found")
            return
        
        track = data['track']
        asset = data['asset']
        analysis = data['analysis']
        
        print(f"\n🎵 Track {track_id}: {track.title}")
        print("=" * 60)
        
        # Need analysis first
        if not data['has_analysis']:
            print("❌ No analysis found - cannot generate other data")
            return
        
        if not analysis:
            print("❌ Analysis exists but object is None - skipping")
            return
        
        # Generate tags if missing
        if not data['has_tags']:
            print("   🏷️  Generating tags...")
            try:
                classifier = MoodClassifier()
                mood_data = classifier.classify(
                    analysis.sonic_genome or {},
                    analysis.lyrical_genome or {}
                )
                commercial_tags = classifier.classify_commercial_tags(
                    analysis.sonic_genome or {}
                )
                
                track_tags = TrackTags(
                    track_id=track.id,
                    moods=mood_data.get("moods", []),
                    commercial_tags=commercial_tags,
                    use_cases=mood_data.get("use_cases", []),
                    sounds_like=mood_data.get("sounds_like", [])
                )
                db.add(track_tags)
                await db.commit()
                print(f"      ✅ Generated tags")
            except Exception as e:
                print(f"      ❌ Failed: {e}")
                import traceback
                traceback.print_exc()
        
        # Generate pitch copy if missing
        if not data['has_pitch']:
            print("   📝 Generating pitch copy...")
            try:
                # Get artist name
                artist_name = None
                if track.artist_id:
                    artist_result = await db.execute(
                        select(Artist).where(Artist.id == track.artist_id)
                    )
                    artist = artist_result.scalar_one_or_none()
                    if artist:
                        artist_name = artist.name
                
                pitch_generator = PitchGenerator()
                pitch_data = pitch_generator.generate_pitch(
                    track_title=track.title,
                    artist_name=artist_name or "Unknown Artist",
                    sonic_genome=analysis.sonic_genome,
                    lyrical_genome=analysis.lyrical_genome,
                    tags=None  # Will be generated from analysis
                )
                
                pitch_copy = PitchCopy(
                    track_id=track.id,
                    elevator_pitch=pitch_data.get("elevator_pitch"),
                    short_description=pitch_data.get("short_description"),  # Pitch generator returns this
                    sync_pitch=pitch_data.get("sync_pitch")  # Pitch generator returns this
                )
                db.add(pitch_copy)
                await db.commit()
                print(f"      ✅ Generated pitch copy")
            except Exception as e:
                print(f"      ❌ Failed: {e}")
                import traceback
                traceback.print_exc()
        
        # Generate viral segments if missing and audio exists
        if not data['has_viral'] and data['has_audio']:
            print("   🎯 Generating viral segments...")
            try:
                detector = ViralHookDetector()
                viral_result = detector.detect_viral_segments(
                    asset.audio_path,
                    segment_duration=15.0,
                    top_n=5
                )
                
                if viral_result.get("viral_segments"):
                    hook_data = dict(analysis.hook_data) if analysis.hook_data else {}
                    hook_data["viral_segments"] = viral_result["viral_segments"]
                    analysis.hook_data = hook_data
                    await db.commit()
                    await db.refresh(analysis)
                    print(f"      ✅ Generated {len(viral_result['viral_segments'])} viral segments")
                else:
                    print("      ⚠️  No viral segments detected")
            except Exception as e:
                print(f"      ❌ Failed: {e}")
                import traceback
                traceback.print_exc()
        
        # Generate lyric critique if missing
        if not data['has_lyric_critique']:
            print("   📝 Generating lyric critique...")
            try:
                if not analysis.lyrical_genome:
                    print("      ⚠️  No lyrical_genome - skipping")
                else:
                    # Get lyrics from TrackAsset
                    lyrics_text = ""
                    if asset:
                        lyrics_text = asset.lyrics_text or ""
                    
                    if not lyrics_text:
                        print("      ⚠️  No lyrics text - skipping")
                    else:
                        critic = AILyricCritic()
                        critique = critic.critique(
                            lyrics=lyrics_text,
                            lyrical_genome=analysis.lyrical_genome
                        )
                        
                        analysis.ai_lyric_critique = critique
                        await db.commit()
                        await db.refresh(analysis)
                        print(f"      ✅ Generated lyric critique")
            except Exception as e:
                print(f"      ❌ Failed: {e}")
                import traceback
                traceback.print_exc()


async def main():
    """Check all tracks and fix missing data."""
    async with AsyncSessionLocal() as db:
        # Get all tracks
        result = await db.execute(
            select(Track.id, Track.title).order_by(Track.id)
        )
        tracks = result.all()
        
        print(f"Found {len(tracks)} tracks\n")
        print("Checking track data...")
        print("=" * 80)
        print(f"{'ID':<6} | {'Title':<30} | Tags | Pitch | Viral | Critique")
        print("-" * 80)
        
        missing = []
        for track_id, title in tracks:
            data = await check_track_data(track_id, db)
            if not data:
                continue
            
            title_short = (title[:28] + '..') if title and len(title) > 30 else (title or 'N/A')
            tags = "✓" if data['has_tags'] else "✗"
            pitch = "✓" if data['has_pitch'] else "✗"
            viral = "✓" if data['has_viral'] else "✗"
            critique = "✓" if data['has_lyric_critique'] else "✗"
            
            print(f"{track_id:<6} | {title_short:<30} | {tags:4} | {pitch:5} | {viral:5} | {critique:8}")
            
            if not data['has_tags'] or not data['has_pitch'] or not data['has_viral'] or not data['has_lyric_critique']:
                missing.append(track_id)
        
        print("\n" + "=" * 80)
        
        if missing:
            print(f"\n🔧 Generating missing data for {len(missing)} tracks...\n")
            for track_id in missing:
                await generate_missing_data(track_id)
            print("\n✅ Done!")
        else:
            print("\n✅ All tracks have complete data!")


if __name__ == "__main__":
    asyncio.run(main())


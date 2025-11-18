#!/usr/bin/env python3
"""Re-analyze all tracks with AI-enhanced pipeline (ungated features)."""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Load environment variables from root .env
from dotenv import load_dotenv
root_env = Path(__file__).parent.parent.parent / ".env"
load_dotenv(root_env)

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models import Track, TrackAsset, Analysis, Artist
from app.models.track import TrackTags, PitchCopy
from app.services.lyrics.analysis import LyricsAnalyzer
from app.services.ai_tagging.mood_classifier import MoodClassifier
from app.services.ai_tagging.pitch_generator import PitchGenerator


async def reanalyze_all_tracks(skip_confirm=False):
    """Re-analyze all tracks with the new AI-enhanced pipeline."""
    
    print("=" * 80)
    print("🚀 TuneScore: AI-Enhanced Re-Analysis")
    print("=" * 80)
    print()
    print("✨ **NEW AI FEATURES (Ungated!)**:")
    print("   1. AI Section Detection (verses, choruses, bridges)")
    print("   2. AI Lyrics Critique (actionable feedback)")
    print("   3. AI Mood/Commercial Tags (auto-generated)")
    print("   4. AI Pitch Copy (elevator pitch, sync pitch)")
    print()
    print(f"🔑 API Keys available:")
    print(f"   - ANTHROPIC: {'✅' if os.getenv('ANTHROPIC_API_KEY') else '❌'}")
    print(f"   - OPENAI: {'✅' if os.getenv('OPENAI_API_KEY') else '❌'}")
    print(f"   - DEEPSEEK: {'✅' if os.getenv('DEEPSEEK_API_KEY') else '❌'}")
    print()
    
    # Count tracks
    async with AsyncSessionLocal() as db:
        stmt = select(Track)
        result = await db.execute(stmt)
        tracks = result.scalars().all()
        
        print(f"📊 Found {len(tracks)} tracks to re-analyze")
        print()
        
        if not tracks:
            print("❌ No tracks found in database")
            return
        
        # Confirm
        if not skip_confirm:
            response = input(f"⚠️  This will re-analyze ALL {len(tracks)} tracks. Continue? (y/n): ")
            if response.lower() != 'y':
                print("❌ Cancelled by user")
                return
        else:
            print(f"⚡ Auto-confirmed: Re-analyzing all {len(tracks)} tracks...")
        
        print()
        print("=" * 80)
        print()
        
        total_cost = 0.0
        success_count = 0
        error_count = 0
        
        for i, track in enumerate(tracks, 1):
            print(f"[{i}/{len(tracks)}] 🎵 {track.title}")
            
            # Create new session for each track (to avoid transaction errors)
            async with AsyncSessionLocal() as track_db:
                try:
                    # Get track asset
                    stmt = select(TrackAsset).where(TrackAsset.track_id == track.id)
                    result = await track_db.execute(stmt)
                    asset = result.scalar_one_or_none()
                    
                    # Get artist
                    artist = None
                    if track.artist_id:
                        stmt = select(Artist).where(Artist.id == track.artist_id)
                        result = await track_db.execute(stmt)
                        artist = result.scalar_one_or_none()
                    
                    # Re-analyze lyrics with AI
                    lyrical_genome = None
                    track_cost = 0.0
                    
                    if asset and asset.lyrics_text:
                        print(f"   🤖 Running AI-enhanced lyrical analysis...")
                        analyzer = LyricsAnalyzer()
                        lyrical_genome = analyzer.analyze_lyrics(
                            asset.lyrics_text,
                            track_title=track.title,
                            artist_name=artist.name if artist else ""
                        )
                    
                    # Extract costs (if available)
                    if lyrical_genome:
                        # Section detection cost (from ai_critique if present)
                        if "ai_critique" in lyrical_genome and lyrical_genome["ai_critique"]:
                            critique_cost = lyrical_genome["ai_critique"].get("cost", 0)
                            track_cost += critique_cost
                            print(f"      ✅ Lyrics critique: ${critique_cost:.4f}")
                        
                        sections = lyrical_genome.get("sections", [])
                        structure = lyrical_genome.get("structure", {}).get("pattern", "N/A")
                        print(f"      ✅ {len(sections)} sections: {structure[:60]}...")
                
                    # Update analysis
                    stmt = select(Analysis).where(Analysis.track_id == track.id).order_by(Analysis.created_at.desc())
                    result = await track_db.execute(stmt)
                    analysis = result.scalar_one_or_none()
                
                    if analysis and lyrical_genome:
                        analysis.lyrical_genome = lyrical_genome
                    
                    # Generate tags (rule-based, no cost)
                    print(f"   🏷️  Generating tags...")
                    try:
                        classifier = MoodClassifier()
                        mood_data = classifier.classify(
                            analysis.sonic_genome or {},
                            lyrical_genome
                        )
                        commercial_tags = classifier.classify_commercial_tags(
                            analysis.sonic_genome or {}
                        )
                        
                        # Update or create TrackTags
                        stmt = select(TrackTags).where(TrackTags.track_id == track.id)
                        result = await track_db.execute(stmt)
                        track_tags = result.scalar_one_or_none()
                        
                        if track_tags:
                            track_tags.moods = mood_data.get("moods", [])
                            track_tags.commercial_tags = commercial_tags
                            track_tags.use_cases = mood_data.get("use_cases", [])
                            track_tags.sounds_like = mood_data.get("sounds_like", [])
                        else:
                            track_tags = TrackTags(
                                track_id=track.id,
                                moods=mood_data.get("moods", []),
                                commercial_tags=commercial_tags,
                                use_cases=mood_data.get("use_cases", []),
                                sounds_like=mood_data.get("sounds_like", [])
                            )
                            track_db.add(track_tags)
                        
                        print(f"      ✅ {len(track_tags.moods)} moods, {len(commercial_tags)} tags")
                    except Exception as e:
                        print(f"      ⚠️  Tag generation failed: {e}")
                    
                    # Generate pitch copy (AI, has cost)
                    print(f"   📝 Generating AI pitch copy...")
                    try:
                        pitch_generator = PitchGenerator()
                        pitch_data = pitch_generator.generate_pitch(
                            track_title=track.title,
                            artist_name=artist.name if artist else "",
                            sonic_genome=analysis.sonic_genome or {},
                            lyrical_genome=lyrical_genome,
                            tags={
                                "moods": track_tags.moods if track_tags else [],
                                "commercial_tags": track_tags.commercial_tags if track_tags else [],
                                "sounds_like": track_tags.sounds_like if track_tags else [],
                            } if track_tags else None
                        )
                        
                        pitch_cost = pitch_data.get("cost", 0)
                        track_cost += pitch_cost
                        
                        # Update or create PitchCopy
                        stmt = select(PitchCopy).where(PitchCopy.track_id == track.id)
                        result = await track_db.execute(stmt)
                        pitch_copy = result.scalar_one_or_none()
                        
                        if pitch_copy:
                            pitch_copy.elevator_pitch = pitch_data.get("elevator_pitch")
                            pitch_copy.short_description = pitch_data.get("short_description")
                            pitch_copy.sync_pitch = pitch_data.get("sync_pitch")
                            pitch_copy.cost = pitch_cost
                            pitch_copy.generated_at = pitch_data.get("generated_at")
                        else:
                            pitch_copy = PitchCopy(
                                track_id=track.id,
                                elevator_pitch=pitch_data.get("elevator_pitch"),
                                short_description=pitch_data.get("short_description"),
                                sync_pitch=pitch_data.get("sync_pitch"),
                                cost=pitch_cost,
                                generated_at=pitch_data.get("generated_at")
                            )
                            track_db.add(pitch_copy)
                        
                        print(f"      ✅ Pitch copy generated: ${pitch_cost:.4f}")
                    except ValueError as e:
                        print(f"      ⚠️  Pitch generation unavailable (no AI key)")
                    except Exception as e:
                        print(f"      ⚠️  Pitch generation failed: {e}")
                    
                    # Update AI costs in analysis
                    if analysis:
                        analysis.ai_costs = {
                            "lyrics_critique": lyrical_genome.get("ai_critique", {}).get("cost", 0) if lyrical_genome and lyrical_genome.get("ai_critique") else 0,
                            "pitch_copy": pitch_cost if 'pitch_cost' in locals() else 0,
                            "total": track_cost
                        }
                        
                        await track_db.commit()
                        
                        total_cost += track_cost
                        success_count += 1
                        print(f"   ✅ Complete! Track cost: ${track_cost:.4f}")
                    else:
                        print(f"   ⚠️  No analysis found, skipping")
                    
                except Exception as e:
                    await track_db.rollback()
                    error_count += 1
                    print(f"   ❌ Error: {e}")
                
                print()
        
        # Summary
        print("=" * 80)
        print("📊 **RE-ANALYSIS COMPLETE**")
        print("=" * 80)
        print(f"✅ Success: {success_count}/{len(tracks)} tracks")
        print(f"❌ Errors: {error_count}/{len(tracks)} tracks")
        print(f"💰 Total AI Cost: ${total_cost:.4f}")
        print(f"📊 Average Cost/Track: ${total_cost / success_count:.4f}" if success_count > 0 else "")
        print()
        print("🎉 All tracks now have:")
        print("   - AI-detected song sections")
        print("   - AI lyrics critique with ratings")
        print("   - Auto-generated mood/commercial tags")
        print("   - AI-generated pitch copy for sync licensing")
        print()
        print("🚀 No more button clicking required!")


async def main():
    # Check for --yes flag
    skip_confirm = "--yes" in sys.argv or "-y" in sys.argv
    await reanalyze_all_tracks(skip_confirm=skip_confirm)


if __name__ == "__main__":
    asyncio.run(main())


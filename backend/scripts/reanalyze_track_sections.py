#!/usr/bin/env python3
"""Re-analyze track with AI-powered section detection."""

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
from app.services.lyrics.analysis import LyricsAnalyzer


async def reanalyze_track(track_id: int):
    """Re-analyze a track's lyrics with AI section detection."""
    async with AsyncSessionLocal() as db:
        # Get track, asset, and artist
        stmt = select(Track, TrackAsset, Artist).join(
            TrackAsset, Track.id == TrackAsset.track_id
        ).outerjoin(
            Artist, Track.artist_id == Artist.id
        ).where(Track.id == track_id)
        
        result = await db.execute(stmt)
        row = result.first()
        
        if not row:
            print(f"❌ Track {track_id} not found")
            return
        
        track, asset, artist = row
        
        print(f"\n📝 Re-analyzing: {track.title}")
        print(f"👤 Artist: {artist.name if artist else 'Unknown'}")
        print(f"🔑 API Keys available:")
        print(f"   - ANTHROPIC: {'✅' if os.getenv('ANTHROPIC_API_KEY') else '❌'}")
        print(f"   - OPENAI: {'✅' if os.getenv('OPENAI_API_KEY') else '❌'}")
        print(f"   - DEEPSEEK: {'✅' if os.getenv('DEEPSEEK_API_KEY') else '❌'}")
        
        if not asset or not asset.lyrics_text:
            print("❌ No lyrics found for this track")
            return
        
        # Analyze lyrics with AI
        print("\n🤖 Running AI-powered section detection...")
        analyzer = LyricsAnalyzer()
        lyrical_genome = analyzer.analyze_lyrics(
            asset.lyrics_text,
            track_title=track.title,
            artist_name=artist.name if artist else ""
        )
        
        # Get existing analysis
        stmt = select(Analysis).where(Analysis.track_id == track_id).order_by(Analysis.created_at.desc())
        result = await db.execute(stmt)
        analysis = result.scalar_one_or_none()
        
        if analysis:
            # Update existing analysis
            print("✅ Updating existing analysis...")
            analysis.lyrical_genome = lyrical_genome
        else:
            # Create new analysis
            print("✅ Creating new analysis...")
            analysis = Analysis(
                track_id=track_id,
                sonic_genome={},
                lyrical_genome=lyrical_genome,
                hook_data={},
                tunescore={},
                genre_predictions={}
            )
            db.add(analysis)
        
        await db.commit()
        
        # Display results
        print("\n✨ Analysis Complete!")
        print(f"\n📊 Structure Pattern:")
        if "structure" in lyrical_genome and "pattern" in lyrical_genome["structure"]:
            print(f"   {lyrical_genome['structure']['pattern']}")
        
        print(f"\n📚 Sections ({len(lyrical_genome.get('sections', []))}):")
        for i, section in enumerate(lyrical_genome.get("sections", []), 1):
            print(f"   {i}. {section['type']} ({section['line_count']} lines)")
        
        print(f"\n💰 Cost: ${lyrical_genome.get('ai_cost', 0):.4f}")
        print(f"🔧 Provider: {lyrical_genome.get('ai_provider', 'heuristic')}")


async def main():
    if len(sys.argv) < 2:
        print("Usage: python reanalyze_track_sections.py <track_id>")
        print("\nExample: python reanalyze_track_sections.py 11")
        sys.exit(1)
    
    track_id = int(sys.argv[1])
    await reanalyze_track(track_id)


if __name__ == "__main__":
    asyncio.run(main())


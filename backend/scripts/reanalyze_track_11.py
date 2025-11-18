#!/usr/bin/env python3
"""
Re-analyze Track 11 ("The Devil Went Down to Georgia") with hybrid ML genre detection.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models import Analysis, Track, TrackAsset
from app.services.classification import detect_genre_hybrid
from app.services.lyrics.analysis import analyze_lyrics


async def reanalyze_track_11():
    """Re-analyze track 11 with hybrid genre detection."""
    
    # Create engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )
    
    # Create session factory
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    track_id = 11
    
    try:
        async with async_session() as db:
            # Get track and asset
            stmt = select(Track, TrackAsset).join(
                TrackAsset, Track.id == TrackAsset.track_id
            ).where(Track.id == track_id)
            
            row = (await db.execute(stmt)).first()
            
            if not row:
                print(f"❌ Track {track_id} or asset not found")
                return
            
            track, asset = row
            
            if not asset.audio_path or not Path(asset.audio_path).exists():
                print(f"❌ Audio file not found: {asset.audio_path}")
                return
            
            # Get existing analysis
            stmt = select(Analysis).where(Analysis.track_id == track_id)
            analysis = (await db.execute(stmt)).scalar_one_or_none()
            
            if not analysis:
                print(f"❌ No analysis record found for track {track_id}")
                return
            
            print("=" * 70)
            print(f"Re-analyzing Track {track_id}: {track.title}")
            print("=" * 70)
            
            # Re-analyze lyrics with new heuristic section detection
            print("\n📝 Re-analyzing lyrics with heuristic section detection...")
            if asset.lyrics_text:
                try:
                    lyrical_genome = analyze_lyrics(asset.lyrics_text)
                    
                    old_sections = len(analysis.lyrical_genome.get('sections', [])) if analysis.lyrical_genome else 0
                    new_sections = len(lyrical_genome.get('sections', []))
                    
                    analysis.lyrical_genome = lyrical_genome
                    
                    print(f"   ✅ Sections detected: {old_sections} → {new_sections}")
                    
                    if lyrical_genome.get('sections'):
                        print(f"   Section types:")
                        for section in lyrical_genome['sections']:
                            print(f"     - {section['type'].title()}: {section['line_count']} lines")
                    
                except Exception as e:
                    print(f"   ❌ Lyrics analysis failed: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("   ⊘ No lyrics available")
            
            # Show old genre
            old_genre = None
            old_confidence = None
            if analysis.genre_predictions and 'predictions' in analysis.genre_predictions:
                old_genre = analysis.genre_predictions['predictions'][0]['genre']
                old_confidence = analysis.genre_predictions['predictions'][0]['confidence']
            
            print(f"\n📊 OLD GENRE:")
            if old_genre:
                print(f"   {old_genre} ({old_confidence:.0f}%)")
                if len(analysis.genre_predictions['predictions']) >= 3:
                    top3_str = ', '.join([f"{p['genre']} ({p['confidence']:.0f}%)" for p in analysis.genre_predictions['predictions'][:3]])
                    print(f"   Top 3: {top3_str}")
            else:
                print("   N/A")
            
            # Re-detect genre using hybrid ML + instrument detection
            print("\n🔍 Running hybrid genre detection (ML + instruments)...")
            try:
                genre_data = detect_genre_hybrid(
                    asset.audio_path,
                    analysis.sonic_genome or {},
                    analysis.lyrical_genome
                )
                
                analysis.genre_predictions = genre_data
                
                print(f"\n✅ NEW GENRE:")
                if genre_data and 'predictions' in genre_data:
                    top_genre = genre_data['predictions'][0]
                    method = genre_data.get('method', 'heuristic')
                    print(f"   {top_genre['genre']} ({top_genre['confidence']:.0f}%)")
                    print(f"   Method: {method}")
                    
                    # Show top 3 predictions
                    if len(genre_data['predictions']) >= 3:
                        top3_str = ', '.join([f"{p['genre']} ({p['confidence']:.0f}%)" for p in genre_data['predictions'][:3]])
                        print(f"   Top 3: {top3_str}")
                    
                    # Show instrument detections
                    if 'components' in genre_data and 'instruments' in genre_data['components']:
                        instruments = genre_data['components']['instruments'].get('instruments', {})
                        print(f"\n🎻 DETECTED INSTRUMENTS:")
                        for inst, score in instruments.items():
                            if score > 0.001:  # Only show meaningful scores
                                print(f"   {inst}: {score*100:.2f}%")
                
                # Commit changes
                await db.commit()
                
                print(f"\n✅ Track {track_id} updated successfully!")
                print(f"\n🌐 View results: https://music.quilty.app/tracks/{track_id}")
                
            except Exception as e:
                print(f"\n❌ Hybrid genre detection failed: {e}")
                import traceback
                traceback.print_exc()
                await db.rollback()
    
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(reanalyze_track_11())


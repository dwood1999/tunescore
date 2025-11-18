#!/usr/bin/env python3
"""
Re-analyze all existing tracks with updated features.

This script:
1. Extracts quality metrics (pitch, timing, harmonic coherence)
2. Recalculates TuneScore with improved algorithm
3. Adds songwriting quality analysis
4. Properly manages database connections (no hanging connections)
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models import Analysis, Track, TrackAsset
from app.services.audio.feature_extraction import AudioFeatureExtractor
from app.services.classification import detect_genre, detect_genre_hybrid
from app.services.lyrics.analysis import analyze_lyrics
from app.services.scoring import calculate_tunescore


async def reanalyze_track(track_id: int, db: AsyncSession) -> dict:
    """
    Re-analyze a single track with all new features.
    
    Returns status dict with results.
    """
    result = {
        "track_id": track_id,
        "success": False,
        "updated_fields": [],
        "errors": [],
    }
    
    try:
        # Get track and asset
        stmt = select(Track, TrackAsset).join(
            TrackAsset, Track.id == TrackAsset.track_id
        ).where(Track.id == track_id)
        
        row = (await db.execute(stmt)).first()
        
        if not row:
            result["errors"].append("Track or asset not found")
            return result
        
        track, asset = row
        
        if not asset.audio_path or not Path(asset.audio_path).exists():
            result["errors"].append(f"Audio file not found: {asset.audio_path}")
            return result
        
        # Get existing analysis
        stmt = select(Analysis).where(Analysis.track_id == track_id)
        analysis = (await db.execute(stmt)).scalar_one_or_none()
        
        if not analysis:
            result["errors"].append("No analysis record found")
            return result
        
        print(f"\n{'='*60}")
        print(f"Re-analyzing Track {track_id}: {track.title}")
        print(f"{'='*60}")
        
        # Re-extract sonic genome with new context-aware metrics (CRITICAL!)
        print("→ Re-extracting sonic genome with context-aware metrics...")
        try:
            extractor = AudioFeatureExtractor()
            sonic_genome = extractor.extract_sonic_genome(asset.audio_path)
            
            old_dance = analysis.sonic_genome.get('danceability', 0) if analysis.sonic_genome else 0
            new_dance = sonic_genome.get('danceability', 0)
            
            analysis.sonic_genome = sonic_genome
            result["updated_fields"].append("sonic_genome")
            
            print(f"  ✓ Sonic Genome updated")
            print(f"    - Danceability: {old_dance:.2f} → {new_dance:.2f}")
            print(f"    - Timing Precision: {sonic_genome.get('timing_precision_score', 0):.0f}/100")
            print(f"    - Harmonic Coherence: {sonic_genome.get('harmonic_coherence_score', 0):.0f}/100")
            
        except Exception as e:
            result["errors"].append(f"Sonic genome extraction failed: {e}")
            print(f"  ✗ Sonic genome extraction failed: {e}")
        
        # Extract quality metrics (NEW!)
        print("→ Extracting quality metrics...")
        try:
            extractor = AudioFeatureExtractor()
            quality_metrics = extractor.extract_quality_metrics(asset.audio_path)
            
            analysis.quality_metrics = quality_metrics
            result["updated_fields"].append("quality_metrics")
            
            print(f"  ✓ Quality: {quality_metrics['overall_quality']:.0f}/100 ({quality_metrics['quality_grade']})")
            print(f"    - Pitch: {quality_metrics['pitch_accuracy']:.0f}/100")
            print(f"    - Timing: {quality_metrics['timing_precision']:.0f}/100")
            print(f"    - Harmonic: {quality_metrics['harmonic_coherence']:.0f}/100")
            
        except Exception as e:
            result["errors"].append(f"Quality metrics failed: {e}")
            print(f"  ✗ Quality metrics failed: {e}")
        
        # Recalculate TuneScore with improved algorithm
        print("→ Recalculating TuneScore...")
        try:
            tunescore_data = calculate_tunescore(
                analysis.sonic_genome or {},
                analysis.lyrical_genome,
                analysis.hook_data,
            )
            
            old_score = analysis.tunescore.get('overall_score', 'N/A') if analysis.tunescore else 'N/A'
            analysis.tunescore = tunescore_data
            result["updated_fields"].append("tunescore")
            
            print(f"  ✓ TuneScore: {old_score} → {tunescore_data['overall_score']:.0f} ({tunescore_data['grade']})")
            
        except Exception as e:
            result["errors"].append(f"TuneScore failed: {e}")
            print(f"  ✗ TuneScore failed: {e}")
        
        # Re-analyze lyrics with songwriting quality (NEW!)
        if asset.lyrics_text:
            print("→ Re-analyzing lyrics with songwriting quality...")
            try:
                lyrical_genome = analyze_lyrics(asset.lyrics_text)
                
                old_sw_score = None
                if analysis.lyrical_genome and 'songwriting_quality' in analysis.lyrical_genome:
                    old_sw_score = analysis.lyrical_genome['songwriting_quality'].get('overall_score')
                
                analysis.lyrical_genome = lyrical_genome
                result["updated_fields"].append("lyrical_genome")
                
                if lyrical_genome.get('songwriting_quality'):
                    sw_score = lyrical_genome['songwriting_quality']['overall_score']
                    sw_grade = lyrical_genome['songwriting_quality']['grade']
                    print(f"  ✓ Songwriting: {old_sw_score or 'N/A'} → {sw_score:.0f} ({sw_grade})")
                
            except Exception as e:
                result["errors"].append(f"Lyrics analysis failed: {e}")
                print(f"  ✗ Lyrics analysis failed: {e}")
        else:
            print("  ⊘ No lyrics available")
        
        # Re-detect genre using hybrid ML + instrument detection
        print("→ Re-detecting genre (hybrid ML + instruments)...")
        try:
            genre_data = detect_genre_hybrid(
                asset.audio_path,
                analysis.sonic_genome or {},
                analysis.lyrical_genome
            )
            
            old_genre = None
            if analysis.genre_predictions and 'predictions' in analysis.genre_predictions:
                old_genre = analysis.genre_predictions['predictions'][0]['genre']
            
            analysis.genre_predictions = genre_data
            result["updated_fields"].append("genre_predictions")
            
            if genre_data and 'predictions' in genre_data:
                top_genre = genre_data['predictions'][0]
                method = genre_data.get('method', 'heuristic')
                print(f"  ✓ Genre: {old_genre or 'N/A'} → {top_genre['genre']} ({top_genre['confidence']:.0f}%)")
                print(f"    Method: {method}")
                
                # Show top 3 predictions
                if len(genre_data['predictions']) >= 3:
                    top3_str = ', '.join([f"{p['genre']} ({p['confidence']:.0f}%)" for p in genre_data['predictions'][:3]])
                    print(f"    Top 3: {top3_str}")
            
        except Exception as e:
            result["errors"].append(f"Genre detection failed: {e}")
            print(f"  ✗ Hybrid genre detection failed: {e}")
            print(f"    Falling back to heuristic...")
            try:
                genre_data = detect_genre(analysis.sonic_genome or {}, analysis.lyrical_genome)
                analysis.genre_predictions = genre_data
                result["updated_fields"].append("genre_predictions")
            except Exception as e2:
                print(f"  ✗ Fallback also failed: {e2}")
        
        # Commit changes (properly detach)
        await db.commit()
        await db.refresh(analysis)
        
        result["success"] = True
        print(f"✓ Track {track_id} updated successfully!")
        
    except Exception as e:
        result["errors"].append(f"Unexpected error: {e}")
        print(f"✗ Track {track_id} failed: {e}")
        await db.rollback()
    
    return result


async def reanalyze_all_tracks():
    """Re-analyze all tracks with proper connection management."""
    
    # Create engine with proper pool settings
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_pre_ping=True,  # Verify connections before using
        pool_recycle=3600,   # Recycle connections after 1 hour
        pool_size=5,         # Small pool for batch processing
        max_overflow=0,      # No overflow connections
    )
    
    # Create session factory
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,  # Don't expire objects after commit
    )
    
    try:
        # Get list of all track IDs (separate session)
        print("Fetching track list...")
        async with async_session() as db:
            stmt = select(Track.id, Track.title).order_by(Track.id)
            result = await db.execute(stmt)
            tracks = result.all()
        
        print(f"\nFound {len(tracks)} tracks to re-analyze\n")
        
        if not tracks:
            print("No tracks found!")
            return
        
        # Process each track with its own session
        results = []
        for track_id, title in tracks:
            # Create fresh session for each track
            async with async_session() as db:
                result = await reanalyze_track(track_id, db)
                results.append(result)
            
            # Small delay to avoid overwhelming the system
            await asyncio.sleep(0.1)
        
        # Print summary
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful
        
        print(f"Total tracks: {len(results)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        
        if failed > 0:
            print(f"\nFailed tracks:")
            for r in results:
                if not r["success"]:
                    print(f"  - Track {r['track_id']}: {', '.join(r['errors'])}")
        
        # Show what was updated
        all_fields = set()
        for r in results:
            all_fields.update(r["updated_fields"])
        
        print(f"\nUpdated fields across all tracks:")
        for field in sorted(all_fields):
            count = sum(1 for r in results if field in r["updated_fields"])
            print(f"  - {field}: {count}/{len(results)} tracks")
        
        print(f"\n✅ Re-analysis complete!")
        
    finally:
        # Properly close all connections
        await engine.dispose()
        print("\n🔌 Database connections closed")


if __name__ == "__main__":
    print("="*60)
    print("TuneScore - Track Re-Analysis Script")
    print("="*60)
    print("\nThis will re-analyze all tracks with:")
    print("  • Quality metrics (pitch, timing, harmonic coherence)")
    print("  • Improved TuneScore algorithm")
    print("  • Songwriting quality analysis")
    print("  • Updated genre detection")
    print()
    
    # Run the re-analysis
    asyncio.run(reanalyze_all_tracks())


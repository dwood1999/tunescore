#!/usr/bin/env python3
"""
Test script for upload and analysis functionality.
Tests the complete upload → analysis pipeline.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import AsyncSessionLocal
from backend.app.models import Track, Analysis, TrackAsset
from backend.app.services.audio.feature_extraction import extract_audio_features


async def check_recent_uploads():
    """Check recent uploads and their analysis status."""
    print("\n=== Checking Recent Uploads ===")
    
    async with AsyncSessionLocal() as db:
        # Get last 5 tracks
        stmt = select(Track).order_by(Track.id.desc()).limit(5)
        result = await db.execute(stmt)
        tracks = result.scalars().all()
        
        if not tracks:
            print("❌ No tracks found in database")
            return
        
        print(f"✅ Found {len(tracks)} recent tracks:\n")
        
        for track in tracks:
            print(f"Track ID: {track.id}")
            print(f"  Title: {track.title}")
            print(f"  Duration: {track.duration}s" if track.duration else "  Duration: N/A")
            print(f"  Created: {track.created_at}")
            
            # Check for analysis
            stmt = select(Analysis).where(Analysis.track_id == track.id)
            result = await db.execute(stmt)
            analysis = result.scalar_one_or_none()
            
            if analysis:
                print(f"  ✅ Analysis exists")
                print(f"    - Sonic Genome: {'✅' if analysis.sonic_genome else '❌'}")
                print(f"    - Lyrical Genome: {'✅' if analysis.lyrical_genome else '❌'}")
                print(f"    - TuneScore: {'✅' if analysis.tunescore else '❌'}")
                print(f"    - Hook Data: {'✅' if analysis.hook_data else '❌'}")
                print(f"    - Quality Metrics: {'✅' if analysis.quality_metrics else '❌'}")
                print(f"    - Mastering Quality: {'✅' if analysis.mastering_quality else '❌'}")
                print(f"    - Chord Analysis: {'✅' if analysis.chord_analysis else '❌'}")
                
                if analysis.tunescore:
                    score = analysis.tunescore.get("overall_score", "N/A")
                    grade = analysis.tunescore.get("grade", "N/A")
                    print(f"    - TuneScore: {score} (Grade: {grade})")
            else:
                print(f"  ❌ No analysis found")
            
            # Check for audio file
            stmt = select(TrackAsset).where(TrackAsset.track_id == track.id)
            result = await db.execute(stmt)
            asset = result.scalar_one_or_none()
            
            if asset:
                # Try both relative and absolute paths
                audio_path = Path(asset.audio_path)
                if not audio_path.is_absolute():
                    # Try backend/files first
                    backend_path = Path(__file__).parent / "backend" / asset.audio_path
                    if backend_path.exists():
                        audio_path = backend_path
                    else:
                        # Try root files
                        root_path = Path(__file__).parent / asset.audio_path
                        if root_path.exists():
                            audio_path = root_path
                
                exists = audio_path.exists()
                print(f"  Audio File: {'✅' if exists else '❌'} {asset.audio_path}")
                if exists:
                    size_mb = audio_path.stat().st_size / (1024 * 1024)
                    print(f"    Size: {size_mb:.2f} MB")
                    print(f"    Full path: {audio_path}")
            else:
                print(f"  ❌ No audio asset found")
            
            print()


async def test_audio_analysis():
    """Test audio analysis on an existing file."""
    print("\n=== Testing Audio Analysis ===")
    
    async with AsyncSessionLocal() as db:
        # Find track 17 (recent upload with incomplete analysis)
        stmt = select(TrackAsset).where(TrackAsset.track_id == 17)
        result = await db.execute(stmt)
        asset = result.scalar_one_or_none()
        
        if not asset:
            print("❌ Track 17 asset not found")
            return
        
        # Resolve path
        audio_path = Path(asset.audio_path)
        if not audio_path.is_absolute():
            backend_path = Path(__file__).parent / "backend" / asset.audio_path
            if backend_path.exists():
                audio_path = backend_path
        
        if not audio_path.exists():
            print(f"❌ Audio file not found: {audio_path}")
            return
        
        print(f"✅ Testing analysis on: {audio_path}")
        print(f"   Size: {audio_path.stat().st_size / (1024 * 1024):.2f} MB")
        
        try:
            print("   Running extract_audio_features()...")
            sonic_genome, hook_data, quality_metrics, mastering_quality, chord_analysis = extract_audio_features(str(audio_path))
            
            print("   ✅ Audio analysis completed!")
            print(f"   - Sonic Genome keys: {len(sonic_genome)}")
            print(f"   - Hook Data keys: {len(hook_data)}")
            print(f"   - Quality Metrics keys: {len(quality_metrics)}")
            print(f"   - Mastering Quality keys: {len(mastering_quality)}")
            print(f"   - Chord Analysis keys: {len(chord_analysis)}")
            
            if sonic_genome.get("duration"):
                print(f"   - Duration: {sonic_genome['duration']:.2f}s")
            
        except Exception as e:
            print(f"   ❌ Analysis failed: {e}")
            import traceback
            traceback.print_exc()


async def check_upload_endpoint():
    """Check upload endpoint configuration."""
    print("\n=== Checking Upload Endpoint Configuration ===")
    
    from backend.app.api.routers.tracks import (
        ALLOWED_AUDIO_EXTENSIONS,
        MAX_FILE_SIZE,
        STORAGE_DIR
    )
    
    print(f"✅ Allowed extensions: {', '.join(ALLOWED_AUDIO_EXTENSIONS)}")
    print(f"✅ Max file size: {MAX_FILE_SIZE / (1024 * 1024):.0f} MB")
    print(f"✅ Storage directory: {STORAGE_DIR.absolute()}")
    print(f"   Exists: {'✅' if STORAGE_DIR.exists() else '❌'}")
    
    if STORAGE_DIR.exists():
        # Count files
        total_files = sum(1 for _ in STORAGE_DIR.rglob("*") if _.is_file())
        total_size = sum(f.stat().st_size for f in STORAGE_DIR.rglob("*") if f.is_file())
        print(f"   Total files: {total_files}")
        print(f"   Total size: {total_size / (1024 * 1024):.2f} MB")


async def check_analysis_components():
    """Check if analysis components are available."""
    print("\n=== Checking Analysis Components ===")
    
    components = {
        "librosa": "Audio feature extraction",
        "soundfile": "Audio file I/O",
        "numpy": "Numerical operations",
        "scipy": "Signal processing",
    }
    
    for module, description in components.items():
        try:
            __import__(module)
            print(f"✅ {module}: {description}")
        except ImportError:
            print(f"❌ {module}: {description} - NOT INSTALLED")
    
    # Check optional components
    optional = {
        "essentia": "Enhanced spectral analysis (optional)",
        "demucs": "Stem separation (optional)",
    }
    
    for module, description in optional.items():
        try:
            __import__(module)
            print(f"✅ {module}: {description}")
        except ImportError:
            print(f"⚠️  {module}: {description} - Not installed (optional)")


async def main():
    """Run all tests."""
    print("=" * 60)
    print("TuneScore Upload & Analysis Test Suite")
    print("=" * 60)
    
    try:
        await check_upload_endpoint()
        await check_analysis_components()
        await check_recent_uploads()
        await test_audio_analysis()
        
        print("\n" + "=" * 60)
        print("✅ Test suite completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())


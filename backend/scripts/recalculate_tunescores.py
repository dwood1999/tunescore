#!/usr/bin/env python3
"""Recalculate TuneScores for all tracks with the improved algorithm."""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import select, update
from app.core.config import settings
from app.models import Analysis, Track
from app.services.scoring.tunescore import calculate_tunescore
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


async def recalculate_all():
    """Recalculate TuneScores for all tracks."""
    # Create engine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        # Get all analyses with tracks
        result = await db.execute(
            select(Analysis, Track)
            .join(Track, Analysis.track_id == Track.id)
            .order_by(Track.id)
        )
        rows = result.all()
        
        print(f"Found {len(rows)} tracks to recalculate\n")
        
        for analysis, track in rows:
            # Recalculate TuneScore
            old_score = analysis.tunescore.get('overall_score', 'N/A') if analysis.tunescore else 'N/A'
            old_grade = analysis.tunescore.get('grade', 'N/A') if analysis.tunescore else 'N/A'
            
            new_tunescore = calculate_tunescore(
                analysis.sonic_genome or {},
                analysis.lyrical_genome,
                analysis.hook_data,
            )
            
            new_score = new_tunescore['overall_score']
            new_grade = new_tunescore['grade']
            
            print(f"Track {track.id}: {track.title}")
            print(f"  OLD: {old_score} ({old_grade})")
            print(f"  NEW: {new_score} ({new_grade})")
            
            # Show component changes
            if analysis.tunescore and 'components' in analysis.tunescore:
                old_musicality = analysis.tunescore['components'].get('musicality', {}).get('percentage', 'N/A')
                new_musicality = new_tunescore['components']['musicality']['percentage']
                print(f"  Musicality: {old_musicality}% → {new_musicality}%")
            
            print()
            
            # Update database
            await db.execute(
                update(Analysis)
                .where(Analysis.id == analysis.id)
                .values(tunescore=new_tunescore)
            )
        
        await db.commit()
        print(f"✅ Updated {len(rows)} tracks!")


if __name__ == "__main__":
    asyncio.run(recalculate_all())


#!/usr/bin/env python3
"""Add recent releases (last 7 days) for testing."""

import asyncio
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal
from app.industry_snapshot.models import NewRelease


async def add_recent_releases():
    """Add recent releases to the database."""
    async with AsyncSessionLocal() as db:
        today = date.today()
        
        # Recent releases (last 7 days) - using realistic release dates
        releases_data = [
            ("THE RISE AND FALL OF A MIDWEST PRINCESS (Deluxe)", "Chappell Roan", today - timedelta(days=1)),
            ("Hit Me Hard and Soft (Extended)", "Billie Eilish", today - timedelta(days=2)),
            ("Short n' Sweet (Deluxe)", "Sabrina Carpenter", today - timedelta(days=3)),
            ("Eternal Sunshine (Bonus Tracks)", "Ariana Grande", today - timedelta(days=4)),
            ("Fireworks & Rollerblades (Special Edition)", "Benson Boone", today - timedelta(days=5)),
            ("F-1 Trillion (Deluxe)", "Post Malone", today - timedelta(days=6)),
            ("Die For You (Remixes)", "The Weeknd", today - timedelta(days=7)),
            ("Cowboy Carter (Extended)", "Beyoncé", today - timedelta(days=1)),
            ("One Thing At A Time (Deluxe)", "Morgan Wallen", today - timedelta(days=2)),
            ("Lose Control (Remixes)", "Teddy Swims", today - timedelta(days=3)),
            ("APT. (Remixes)", "ROSÉ, Bruno Mars", today - timedelta(days=4)),
            ("Beautiful Things (Acoustic)", "Benson Boone", today - timedelta(days=5)),
        ]
        
        print(f"Adding {len(releases_data)} recent release entries...")
        for album, artist, release_date in releases_data:
            release = NewRelease(
                artist=artist,
                album_title=album,
                release_date=release_date,
                notable=True,
            )
            db.add(release)
        
        await db.commit()
        print("✅ Recent releases populated successfully!")
        print(f"   - {len(releases_data)} new releases (last 7 days)")


if __name__ == "__main__":
    asyncio.run(add_recent_releases())


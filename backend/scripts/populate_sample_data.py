#!/usr/bin/env python3
"""Populate sample charts and releases data for testing."""

import asyncio
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal
from app.industry_snapshot.models import ChartSnapshot, NewRelease


async def populate_sample_data():
    """Add sample charts and releases to the database."""
    async with AsyncSessionLocal() as db:
        snapshot_date = date.today()
        
        # Sample Billboard Hot 100 data (Top 20)
        billboard_data = [
            ("A Bar Song (Tipsy)", "Shaboozey"),
            ("Die With A Smile", "Lady Gaga & Bruno Mars"),
            ("I Had Some Help", "Post Malone Featuring Morgan Wallen"),
            ("Espresso", "Sabrina Carpenter"),
            ("Beautiful Things", "Benson Boone"),
            ("Not Like Us", "Kendrick Lamar"),
            ("Please Please Please", "Sabrina Carpenter"),
            ("BIRDS OF A FEATHER", "Billie Eilish"),
            ("Taste", "Sabrina Carpenter"),
            ("Good Luck, Babe!", "Chappell Roan"),
            ("Pink Pony Club", "Chappell Roan"),
            ("Lose Control", "Teddy Swims"),
            ("HOT TO GO!", "Chappell Roan"),
            ("Too Sweet", "Hozier"),
            ("Million Dollar Baby", "Tommy Richman"),
            ("Lovin On Me", "Jack Harlow"),
            ("Thick Of It", "KSI Featuring Trippie Redd"),
            ("Espresso", "Sabrina Carpenter"),
            ("Die For You", "The Weeknd"),
            ("TEXAS HOLD 'EM", "Beyonce"),
        ]
        
        print(f"Adding {len(billboard_data)} Billboard chart entries...")
        for idx, (title, artist) in enumerate(billboard_data, 1):
            chart_entry = ChartSnapshot(
                platform="billboard",
                chart_type="hot_100",
                position=idx,
                track_title=title,
                artist=artist,
                snapshot_date=snapshot_date,
            )
            db.add(chart_entry)
        
        # Sample Spotify Top 50 data
        spotify_data = [
            ("Die With A Smile", "Lady Gaga, Bruno Mars"),
            ("BIRDS OF A FEATHER", "Billie Eilish"),
            ("Taste", "Sabrina Carpenter"),
            ("Good Luck, Babe!", "Chappell Roan"),
            ("Espresso", "Sabrina Carpenter"),
            ("Please Please Please", "Sabrina Carpenter"),
            ("Beautiful Things", "Benson Boone"),
            ("Pink Pony Club", "Chappell Roan"),
            ("Not Like Us", "Kendrick Lamar"),
            ("A Bar Song (Tipsy)", "Shaboozey"),
            ("Lose Control", "Teddy Swims"),
            ("Too Sweet", "Hozier"),
            ("TEXAS HOLD 'EM", "Beyoncé"),
            ("Lovin On Me", "Jack Harlow"),
            ("I Had Some Help", "Post Malone, Morgan Wallen"),
            ("HOT TO GO!", "Chappell Roan"),
            ("Casual", "Chappell Roan"),
            ("Cruel Summer", "Taylor Swift"),
            ("APT.", "ROSÉ, Bruno Mars"),
            ("Fortnight", "Taylor Swift, Post Malone"),
        ]
        
        print(f"Adding {len(spotify_data)} Spotify chart entries...")
        for idx, (title, artist) in enumerate(spotify_data, 1):
            chart_entry = ChartSnapshot(
                platform="spotify",
                chart_type="global_top_50",
                position=idx,
                track_title=title,
                artist=artist,
                snapshot_date=snapshot_date,
            )
            db.add(chart_entry)
        
        # Sample New Releases (last 7 days)
        releases_data = [
            ("The Tortured Poets Department: The Anthology", "Taylor Swift", "2024-04-19"),
            ("Hit Me Hard and Soft", "Billie Eilish", "2024-05-17"),
            ("Short n' Sweet", "Sabrina Carpenter", "2024-08-23"),
            ("THE RISE AND FALL OF A MIDWEST PRINCESS", "Chappell Roan", "2023-09-22"),
            ("Eternal Sunshine", "Ariana Grande", "2024-03-08"),
            ("Cowboy Carter", "Beyoncé", "2024-03-29"),
            ("One Thing At A Time", "Morgan Wallen", "2023-03-03"),
            ("Fireworks & Rollerblades", "Benson Boone", "2024-04-05"),
            ("F-1 Trillion", "Post Malone", "2024-08-16"),
            ("Happier Than Ever", "Billie Eilish", "2021-07-30"),
        ]
        
        print(f"Adding {len(releases_data)} new release entries...")
        for album, artist, release_str in releases_data:
            release = NewRelease(
                artist=artist,
                album_title=album,
                release_date=datetime.strptime(release_str, "%Y-%m-%d").date(),
                notable=True,  # Mark as notable releases
            )
            db.add(release)
        
        await db.commit()
        print("✅ Sample data populated successfully!")
        print(f"   - {len(billboard_data)} Billboard chart entries")
        print(f"   - {len(spotify_data)} Spotify chart entries")
        print(f"   - {len(releases_data)} new releases")


if __name__ == "__main__":
    asyncio.run(populate_sample_data())


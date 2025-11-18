"""Industry Pulse data scraper - collects charts, news, and releases."""

import asyncio
import logging
import os
from datetime import date, datetime, timedelta
from typing import Any, Optional

import feedparser
import httpx
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from .ai_digest import IndustryDigestAI
from .models import ChartSnapshot, DailyDigest, IndustryNews, NewRelease

logger = logging.getLogger(__name__)


class IndustryDataScraper:
    """Scrapes music industry data from various sources."""

    def __init__(self, db: AsyncSession):
        """Initialize scraper with database session."""
        self.db = db
        self.ai_digest = None  # Lazy init to avoid errors if no API key

    async def scrape_spotify_charts(self) -> int:
        """Scrape Spotify charts using public API or playlists.
        
        Returns:
            Number of chart entries added
        """
        logger.info("Scraping Spotify charts...")
        count = 0

        try:
            # Using Spotify's public charts data
            # Note: In production, use official Spotify API with credentials
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Spotify Charts CSV endpoint (public, no auth required)
                url = "https://charts.spotify.com/api/tracks/top/global/daily/latest"
                response = await client.get(url)

                if response.status_code != 200:
                    logger.warning(f"Spotify charts returned {response.status_code}")
                    return 0

                data = response.json()
                snapshot_date = date.today()

                # Process entries
                for idx, entry in enumerate(data.get("data", {}).get("items", [])[:50], 1):
                    track = entry.get("track", {})
                    
                    # Check if entry already exists
                    stmt = select(ChartSnapshot).where(
                        ChartSnapshot.platform == "spotify",
                        ChartSnapshot.chart_type == "global_top_50",
                        ChartSnapshot.position == idx,
                        ChartSnapshot.snapshot_date == snapshot_date,
                    )
                    result = await self.db.execute(stmt)
                    existing = result.scalar_one_or_none()

                    if existing:
                        continue  # Skip duplicates

                    # Create new entry
                    chart_entry = ChartSnapshot(
                        platform="spotify",
                        chart_type="global_top_50",
                        position=idx,
                        track_title=track.get("name", ""),
                        artist=", ".join(
                            [a.get("name", "") for a in track.get("artists", [])]
                        ),
                        streams=entry.get("playcount"),
                        movement=entry.get("movement"),  # Position change
                        spotify_id=track.get("id"),
                        snapshot_date=snapshot_date,
                    )
                    self.db.add(chart_entry)
                    count += 1

                if count > 0:
                    await self.db.commit()
                    logger.info(f"Added {count} Spotify chart entries")

        except Exception as e:
            logger.error(f"Failed to scrape Spotify charts: {e}")
            await self.db.rollback()

        return count

    async def scrape_billboard_charts(self) -> int:
        """Scrape Billboard Hot 100 chart.
        
        Returns:
            Number of chart entries added
        """
        logger.info("Scraping Billboard charts...")
        count = 0

        try:
            # Use ScrapeOps proxy if available for better reliability
            scrapeops_key = settings.SCRAPEOPS_API_KEY
            headers = {"User-Agent": "Mozilla/5.0 (compatible; TuneScore/1.0)"}
            
            async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
                if scrapeops_key:
                    # Use ScrapeOps proxy
                    url = f"https://proxy.scrapeops.io/v1/?api_key={scrapeops_key}&url=https://www.billboard.com/charts/hot-100/"
                    logger.info("Using ScrapeOps proxy for Billboard scraping")
                else:
                    url = "https://www.billboard.com/charts/hot-100/"
                    logger.warning("No ScrapeOps API key - using direct scraping")
                
                response = await client.get(url)

                if response.status_code != 200:
                    logger.warning(f"Billboard returned {response.status_code}")
                    return 0

                soup = BeautifulSoup(response.text, "html.parser")
                snapshot_date = date.today()

                # Find chart entries (Billboard's HTML structure)
                chart_items = soup.find_all(
                    "div", class_="o-chart-results-list-row-container"
                )

                for item in chart_items[:100]:
                    try:
                        position_elem = item.find("span", class_="c-label")
                        title_elem = item.find("h3", id=lambda x: x and x.startswith("title"))
                        artist_elem = item.find("span", class_="c-label a-no-trucate")

                        if not all([position_elem, title_elem, artist_elem]):
                            continue

                        position = int(position_elem.text.strip())
                        title = title_elem.text.strip()
                        artist = artist_elem.text.strip()

                        # Check for duplicates
                        stmt = select(ChartSnapshot).where(
                            ChartSnapshot.platform == "billboard",
                            ChartSnapshot.chart_type == "hot_100",
                            ChartSnapshot.position == position,
                            ChartSnapshot.snapshot_date == snapshot_date,
                        )
                        result = await self.db.execute(stmt)
                        existing = result.scalar_one_or_none()

                        if existing:
                            continue

                        chart_entry = ChartSnapshot(
                            platform="billboard",
                            chart_type="hot_100",
                            position=position,
                            track_title=title,
                            artist=artist,
                            snapshot_date=snapshot_date,
                        )
                        self.db.add(chart_entry)
                        count += 1

                    except (ValueError, AttributeError) as e:
                        logger.debug(f"Skipping Billboard entry: {e}")
                        continue

                if count > 0:
                    await self.db.commit()
                    logger.info(f"Added {count} Billboard chart entries")

        except Exception as e:
            logger.error(f"Failed to scrape Billboard charts: {e}")
            await self.db.rollback()

        return count

    async def fetch_news_feeds(self) -> int:
        """Fetch news from RSS feeds.
        
        Returns:
            Number of news articles added
        """
        logger.info("Fetching news feeds...")
        count = 0

        feeds = [
            ("https://www.musicbusinessworldwide.com/feed/", "MBW"),
            ("https://www.billboard.com/feed/", "Billboard"),
            ("https://variety.com/v/music/feed/", "Variety"),
            ("https://www.rollingstone.com/music/feed/", "Rolling Stone"),
        ]

        for feed_url, source in feeds:
            try:
                # Parse RSS feed
                feed = feedparser.parse(feed_url)

                for entry in feed.entries[:10]:  # Limit to 10 most recent
                    try:
                        # Check if article already exists
                        url = entry.get("link", "")
                        if not url:
                            continue

                        stmt = select(IndustryNews).where(IndustryNews.url == url)
                        result = await self.db.execute(stmt)
                        existing = result.scalar_one_or_none()

                        if existing:
                            continue  # Skip duplicates

                        # Parse published date
                        published_at = datetime.now()
                        if hasattr(entry, "published_parsed"):
                            try:
                                published_at = datetime(
                                    *entry.published_parsed[:6]
                                )
                            except (TypeError, ValueError):
                                pass

                        # Get content
                        title = entry.get("title", "")
                        content = entry.get("summary", entry.get("description", ""))

                        # AI summarization (if available)
                        summary = None
                        category = None
                        impact_score = None

                        if self.ai_digest is None:
                            try:
                                self.ai_digest = IndustryDigestAI()
                            except ValueError:
                                logger.warning(
                                    "AI digest not available - skipping summarization"
                                )

                        if self.ai_digest:
                            summary_data = await self.ai_digest.summarize_news_article(
                                title, content, source
                            )
                            summary = summary_data.get("summary")
                            category = summary_data.get("category")
                            impact_score = summary_data.get("impact_score")

                        news_item = IndustryNews(
                            title=title,
                            source=source,
                            url=url,
                            summary=summary or content[:500],
                            category=category,
                            impact_score=impact_score,
                            published_at=published_at,
                        )
                        self.db.add(news_item)
                        count += 1

                        # Commit in batches to avoid overwhelming AI API
                        if count % 5 == 0:
                            await self.db.commit()
                            await asyncio.sleep(1)  # Rate limiting

                    except Exception as e:
                        logger.debug(f"Skipping news entry from {source}: {e}")
                        continue

            except Exception as e:
                logger.error(f"Failed to fetch {source} feed: {e}")
                continue

        if count > 0:
            await self.db.commit()
            logger.info(f"Added {count} news articles")

        return count

    async def fetch_new_releases(self) -> int:
        """Fetch new releases from Spotify.
        
        Note: Requires Spotify API credentials in production.
        Returns:
            Number of releases added
        """
        logger.info("Fetching new releases...")
        count = 0

        try:
            # Placeholder: In production, use spotipy with OAuth
            # For now, we'll create a stub that can be populated via admin panel
            logger.warning(
                "New releases scraping requires Spotify API auth - skipping for now"
            )
            # TODO: Implement with spotipy when credentials are configured

        except Exception as e:
            logger.error(f"Failed to fetch new releases: {e}")

        return count

    async def generate_daily_digest(self) -> Optional[dict[str, Any]]:
        """Generate AI-powered daily digest from collected data.
        
        Returns:
            Digest data or None if failed
        """
        logger.info("Generating daily digest...")

        try:
            today = date.today()

            # Check if digest already exists for today
            stmt = select(DailyDigest).where(DailyDigest.digest_date == today)
            result = await self.db.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                logger.info("Digest already exists for today")
                return None

            # Gather data from last 24 hours
            yesterday = today - timedelta(days=1)

            # Get news
            news_stmt = (
                select(IndustryNews)
                .where(IndustryNews.created_at >= yesterday)
                .order_by(IndustryNews.published_at.desc())
                .limit(20)
            )
            news_result = await self.db.execute(news_stmt)
            news_items = [
                {
                    "title": n.title,
                    "source": n.source,
                    "summary": n.summary,
                    "category": n.category,
                }
                for n in news_result.scalars().all()
            ]

            # Get chart data
            charts_stmt = (
                select(ChartSnapshot)
                .where(ChartSnapshot.snapshot_date == today)
                .limit(10)
            )
            charts_result = await self.db.execute(charts_stmt)
            chart_data = {
                "top_10": [
                    {"position": c.position, "track": c.track_title, "artist": c.artist}
                    for c in charts_result.scalars().all()
                ]
            }

            # Get releases
            releases_stmt = (
                select(NewRelease)
                .where(NewRelease.release_date >= yesterday)
                .limit(20)
            )
            releases_result = await self.db.execute(releases_stmt)
            releases = [
                {"artist": r.artist, "album_title": r.album_title, "notable": r.notable}
                for r in releases_result.scalars().all()
            ]

            # Generate digest with AI
            if self.ai_digest is None:
                try:
                    self.ai_digest = IndustryDigestAI()
                except ValueError as e:
                    logger.error(f"Cannot generate digest: {e}")
                    return None

            digest_data = await self.ai_digest.generate_daily_digest(
                news_items, chart_data, releases
            )

            # Save to database
            digest = DailyDigest(
                digest_date=today,
                summary_text=digest_data.get("summary_text", ""),
                key_highlights=digest_data.get("key_highlights", {}),
                cost=digest_data.get("cost", 0.0),
                tokens=digest_data.get("tokens", {}),
            )
            self.db.add(digest)
            await self.db.commit()

            logger.info(
                f"Generated daily digest (cost: ${digest_data.get('cost', 0):.4f})"
            )
            return digest_data

        except Exception as e:
            logger.error(f"Failed to generate daily digest: {e}")
            await self.db.rollback()
            return None


async def run_scraping_job(db: AsyncSession) -> dict[str, Any]:
    """Orchestrator - run all data collection jobs.
    
    Returns:
        Summary of scraping results
    """
    logger.info("Starting Industry Pulse data scraping job...")
    scraper = IndustryDataScraper(db)

    results = {
        "started_at": datetime.utcnow().isoformat(),
        "charts": {"spotify": 0, "billboard": 0},
        "news": 0,
        "releases": 0,
        "digest": None,
        "errors": [],
    }

    # Run scrapers
    try:
        results["charts"]["spotify"] = await scraper.scrape_spotify_charts()
    except Exception as e:
        results["errors"].append(f"Spotify charts failed: {e}")

    try:
        results["charts"]["billboard"] = await scraper.scrape_billboard_charts()
    except Exception as e:
        results["errors"].append(f"Billboard charts failed: {e}")

    try:
        results["news"] = await scraper.fetch_news_feeds()
    except Exception as e:
        results["errors"].append(f"News feeds failed: {e}")

    try:
        results["releases"] = await scraper.fetch_new_releases()
    except Exception as e:
        results["errors"].append(f"Releases failed: {e}")

    # Generate digest if we have data
    total_items = (
        results["charts"]["spotify"]
        + results["charts"]["billboard"]
        + results["news"]
        + results["releases"]
    )

    if total_items > 0:
        try:
            digest_data = await scraper.generate_daily_digest()
            results["digest"] = (
                "generated" if digest_data else "skipped (already exists)"
            )
        except Exception as e:
            results["errors"].append(f"Digest generation failed: {e}")

    results["completed_at"] = datetime.utcnow().isoformat()
    logger.info(f"Scraping job complete: {results}")

    return results


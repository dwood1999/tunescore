"""Industry Pulse API endpoints."""

import logging
from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import AsyncSessionLocal, get_db
from ..schemas.industry_snapshot import (
    ChartMoversSchema,
    ChartSnapshotSchema,
    DailyDigestSchema,
    IndustryNewsSchema,
    NewReleaseSchema,
)
from .models import ChartSnapshot, DailyDigest, IndustryNews, NewRelease
from .scraper import run_scraping_job

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/digest", response_model=Optional[DailyDigestSchema])
async def get_daily_digest(
    digest_date: Optional[str] = Query(
        None, description="Date in YYYY-MM-DD format (defaults to latest)"
    ),
    db: AsyncSession = Depends(get_db),
) -> Optional[DailyDigestSchema]:
    """Get AI-generated daily digest."""
    try:
        if digest_date:
            # Parse specific date
            target_date = date.fromisoformat(digest_date)
            stmt = select(DailyDigest).where(DailyDigest.digest_date == target_date)
        else:
            # Get latest digest
            stmt = (
                select(DailyDigest).order_by(desc(DailyDigest.digest_date)).limit(1)
            )

        result = await db.execute(stmt)
        digest = result.scalar_one_or_none()

        if not digest:
            return None

        return DailyDigestSchema.model_validate(digest)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
    except Exception as e:
        logger.error(f"Failed to fetch digest: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch digest")


@router.get("/charts", response_model=list[ChartSnapshotSchema])
async def get_charts(
    platform: str = Query("spotify", description="Platform: spotify, apple, billboard"),
    chart_type: str = Query("global_top_50", description="Chart type"),
    limit: int = Query(50, ge=1, le=200, description="Number of results"),
    db: AsyncSession = Depends(get_db),
) -> list[ChartSnapshotSchema]:
    """Get latest chart data."""
    try:
        # Get the most recent snapshot date for this platform/chart
        date_stmt = (
            select(func.max(ChartSnapshot.snapshot_date))
            .where(ChartSnapshot.platform == platform)
            .where(ChartSnapshot.chart_type == chart_type)
        )
        result = await db.execute(date_stmt)
        latest_date = result.scalar_one_or_none()

        if not latest_date:
            return []

        # Get charts for that date
        stmt = (
            select(ChartSnapshot)
            .where(ChartSnapshot.platform == platform)
            .where(ChartSnapshot.chart_type == chart_type)
            .where(ChartSnapshot.snapshot_date == latest_date)
            .order_by(ChartSnapshot.position)
            .limit(limit)
        )

        result = await db.execute(stmt)
        charts = result.scalars().all()

        return [ChartSnapshotSchema.model_validate(chart) for chart in charts]

    except Exception as e:
        logger.error(f"Failed to fetch charts: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch charts")


@router.get("/charts/movers", response_model=ChartMoversSchema)
async def get_chart_movers(
    platform: str = Query("spotify", description="Platform: spotify, apple, billboard"),
    days: int = Query(7, ge=1, le=30, description="Days to look back"),
    limit: int = Query(10, ge=1, le=50, description="Number of movers per category"),
    db: AsyncSession = Depends(get_db),
) -> ChartMoversSchema:
    """Get biggest chart movers (risers and fallers) over the past N days."""
    try:
        # Get the two most recent snapshot dates
        date_stmt = (
            select(ChartSnapshot.snapshot_date)
            .where(ChartSnapshot.platform == platform)
            .distinct()
            .order_by(desc(ChartSnapshot.snapshot_date))
            .limit(2)
        )
        result = await db.execute(date_stmt)
        dates = result.scalars().all()

        if len(dates) < 2:
            return ChartMoversSchema(risers=[], fallers=[])

        latest_date, previous_date = dates[0], dates[1]

        # Get tracks with biggest positive movement (risers)
        risers_stmt = (
            select(ChartSnapshot)
            .where(ChartSnapshot.platform == platform)
            .where(ChartSnapshot.snapshot_date == latest_date)
            .where(ChartSnapshot.movement.isnot(None))
            .where(ChartSnapshot.movement > 0)
            .order_by(desc(ChartSnapshot.movement))
            .limit(limit)
        )
        result = await db.execute(risers_stmt)
        risers = result.scalars().all()

        # Get tracks with biggest negative movement (fallers)
        fallers_stmt = (
            select(ChartSnapshot)
            .where(ChartSnapshot.platform == platform)
            .where(ChartSnapshot.snapshot_date == latest_date)
            .where(ChartSnapshot.movement.isnot(None))
            .where(ChartSnapshot.movement < 0)
            .order_by(ChartSnapshot.movement)
            .limit(limit)
        )
        result = await db.execute(fallers_stmt)
        fallers = result.scalars().all()

        return ChartMoversSchema(
            risers=[ChartSnapshotSchema.model_validate(r) for r in risers],
            fallers=[ChartSnapshotSchema.model_validate(f) for f in fallers],
        )

    except Exception as e:
        logger.error(f"Failed to fetch chart movers: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch chart movers")


@router.get("/news", response_model=list[IndustryNewsSchema])
async def get_industry_news(
    category: Optional[str] = Query(
        None, description="Filter by category: M&A, Signings, Platform, Legal, Tech"
    ),
    days: int = Query(7, ge=1, le=90, description="Days to look back"),
    user_tier: Optional[str] = Query(
        None, description="Filter by relevance: creator, developer, monetizer"
    ),
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    db: AsyncSession = Depends(get_db),
) -> list[IndustryNewsSchema]:
    """Get industry news feed."""
    try:
        cutoff_date = date.today() - timedelta(days=days)

        stmt = (
            select(IndustryNews)
            .where(IndustryNews.published_at >= cutoff_date)
            .order_by(desc(IndustryNews.published_at))
        )

        if category:
            stmt = stmt.where(IndustryNews.category == category)

        # Apply tier-based filtering if specified
        # (This assumes impact_score JSONB has tier scores)
        # We'll add sorting by relevance in a future iteration

        stmt = stmt.limit(limit)

        result = await db.execute(stmt)
        news = result.scalars().all()

        # If user_tier specified, sort by impact score for that tier
        if user_tier and news:
            news_list = list(news)
            news_list.sort(
                key=lambda n: (n.impact_score or {}).get(user_tier, 0), reverse=True
            )
            return [IndustryNewsSchema.model_validate(n) for n in news_list]

        return [IndustryNewsSchema.model_validate(n) for n in news]

    except Exception as e:
        logger.error(f"Failed to fetch news: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch news")


@router.get("/releases", response_model=list[NewReleaseSchema])
async def get_new_releases(
    genre: Optional[str] = Query(None, description="Filter by genre"),
    days: int = Query(7, ge=1, le=90, description="Days to look back"),
    notable_only: bool = Query(False, description="Only show notable releases"),
    limit: int = Query(50, ge=1, le=200, description="Number of results"),
    db: AsyncSession = Depends(get_db),
) -> list[NewReleaseSchema]:
    """Get new music releases."""
    try:
        cutoff_date = date.today() - timedelta(days=days)

        stmt = (
            select(NewRelease)
            .where(NewRelease.release_date >= cutoff_date)
            .order_by(desc(NewRelease.release_date))
        )

        if genre:
            stmt = stmt.where(NewRelease.genre == genre)

        if notable_only:
            stmt = stmt.where(NewRelease.notable == True)

        stmt = stmt.limit(limit)

        result = await db.execute(stmt)
        releases = result.scalars().all()

        return [NewReleaseSchema.model_validate(r) for r in releases]

    except Exception as e:
        logger.error(f"Failed to fetch releases: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch releases")


@router.get("/gear", response_model=list)
async def get_gear_releases() -> list:
    """Get new gear/software releases (Phase 2 - stub for now)."""
    return []


@router.post("/refresh")
async def refresh_data(background_tasks: BackgroundTasks) -> dict[str, str]:
    """Trigger manual data refresh."""
    background_tasks.add_task(_run_refresh_job)
    return {"status": "started", "message": "Data refresh started in background"}


async def _run_refresh_job():
    """Background job to run scraper."""
    logger.info("Starting manual data refresh...")
    async with AsyncSessionLocal() as db:
        try:
            await run_scraping_job(db)
            logger.info("Manual data refresh completed")
        except Exception as e:
            logger.error(f"Manual data refresh failed: {e}")


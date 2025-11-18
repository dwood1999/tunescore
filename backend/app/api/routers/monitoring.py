"""AI Cost Monitoring and Analytics endpoints."""

from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...core.security import get_current_user_id
from ...models import Analysis, Track

router = APIRouter()


@router.get("/ai-costs/summary")
async def get_ai_costs_summary(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze"),
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Get AI cost summary for the authenticated user.
    
    Returns aggregated costs by feature and time period.
    """
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Query user's tracks and their analyses
    stmt = (
        select(Analysis)
        .join(Track, Track.id == Analysis.track_id)
        .where(Track.user_id == current_user_id)
        .where(Analysis.created_at >= start_date)
    )
    
    result = await db.execute(stmt)
    analyses = result.scalars().all()
    
    # Aggregate costs
    total_cost = 0.0
    costs_by_feature: dict[str, float] = {}
    costs_by_model: dict[str, float] = {}
    track_count = 0
    
    for analysis in analyses:
        if analysis.ai_costs:
            track_count += 1
            for feature, cost_data in analysis.ai_costs.items():
                if isinstance(cost_data, dict):
                    cost = cost_data.get('cost', 0.0)
                    model = cost_data.get('model', 'unknown')
                elif isinstance(cost_data, (int, float)):
                    cost = float(cost_data)
                    model = 'unknown'
                else:
                    continue
                
                total_cost += cost
                costs_by_feature[feature] = costs_by_feature.get(feature, 0.0) + cost
                costs_by_model[model] = costs_by_model.get(model, 0.0) + cost
    
    # Calculate averages
    avg_cost_per_track = total_cost / track_count if track_count > 0 else 0.0
    
    return {
        "period_days": days,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "total_cost_usd": round(total_cost, 4),
        "tracks_analyzed": track_count,
        "avg_cost_per_track_usd": round(avg_cost_per_track, 4),
        "costs_by_feature": {
            k: round(v, 4) for k, v in sorted(
                costs_by_feature.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
        },
        "costs_by_model": {
            k: round(v, 4) for k, v in sorted(
                costs_by_model.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
        },
    }


@router.get("/ai-costs/daily")
async def get_daily_ai_costs(
    days: int = Query(default=30, ge=1, le=90, description="Number of days"),
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get daily AI cost breakdown for the authenticated user."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Query user's tracks and analyses
    stmt = (
        select(Analysis)
        .join(Track, Track.id == Analysis.track_id)
        .where(Track.user_id == current_user_id)
        .where(Analysis.created_at >= start_date)
        .order_by(Analysis.created_at)
    )
    
    result = await db.execute(stmt)
    analyses = result.scalars().all()
    
    # Organize by day
    daily_costs: dict[str, float] = {}
    
    for analysis in analyses:
        day_key = analysis.created_at.date().isoformat()
        day_cost = 0.0
        
        if analysis.ai_costs:
            for feature, cost_data in analysis.ai_costs.items():
                if isinstance(cost_data, dict):
                    cost = cost_data.get('cost', 0.0)
                elif isinstance(cost_data, (int, float)):
                    cost = float(cost_data)
                else:
                    continue
                day_cost += cost
        
        daily_costs[day_key] = daily_costs.get(day_key, 0.0) + day_cost
    
    # Format for charting
    dates = []
    costs = []
    for day_key in sorted(daily_costs.keys()):
        dates.append(day_key)
        costs.append(round(daily_costs[day_key], 4))
    
    return {
        "period_days": days,
        "dates": dates,
        "costs_usd": costs,
        "total_cost_usd": round(sum(costs), 4),
    }


@router.get("/ai-costs/tracks")
async def get_track_costs(
    limit: int = Query(default=10, ge=1, le=100),
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Get AI costs per track, sorted by cost (highest first)."""
    # Query user's tracks with analyses
    stmt = (
        select(Track, Analysis)
        .join(Analysis, Track.id == Analysis.track_id, isouter=True)
        .where(Track.user_id == current_user_id)
        .order_by(Track.created_at.desc())
        .limit(limit)
    )
    
    result = await db.execute(stmt)
    rows = result.all()
    
    track_costs = []
    for track, analysis in rows:
        total_cost = 0.0
        features_used = []
        
        if analysis and analysis.ai_costs:
            for feature, cost_data in analysis.ai_costs.items():
                features_used.append(feature)
                if isinstance(cost_data, dict):
                    cost = cost_data.get('cost', 0.0)
                elif isinstance(cost_data, (int, float)):
                    cost = float(cost_data)
                else:
                    continue
                total_cost += cost
        
        track_costs.append({
            "track_id": track.id,
            "track_title": track.title,
            "created_at": track.created_at.isoformat(),
            "total_cost_usd": round(total_cost, 4),
            "features_used": features_used,
        })
    
    # Sort by cost
    track_costs.sort(key=lambda x: x["total_cost_usd"], reverse=True)
    
    return track_costs


@router.get("/ai-costs/budget-status")
async def get_budget_status(
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Check current budget status against configured limits.
    
    Returns daily and per-track spending vs limits.
    """
    from ...core.config import settings
    
    # Get today's costs
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    stmt = (
        select(Analysis)
        .join(Track, Track.id == Analysis.track_id)
        .where(Track.user_id == current_user_id)
        .where(Analysis.created_at >= today_start)
    )
    
    result = await db.execute(stmt)
    analyses = result.scalars().all()
    
    today_total = 0.0
    max_track_cost = 0.0
    
    for analysis in analyses:
        if analysis.ai_costs:
            track_cost = 0.0
            for feature, cost_data in analysis.ai_costs.items():
                if isinstance(cost_data, dict):
                    cost = cost_data.get('cost', 0.0)
                elif isinstance(cost_data, (int, float)):
                    cost = float(cost_data)
                else:
                    continue
                track_cost += cost
            
            today_total += track_cost
            max_track_cost = max(max_track_cost, track_cost)
    
    # Get configured limits
    daily_limit = settings.get_user_daily_max_usd()
    per_analysis_limit = settings.get_analysis_max_usd()
    
    # Calculate percentages
    daily_pct = (today_total / daily_limit * 100) if daily_limit > 0 else 0
    analysis_pct = (max_track_cost / per_analysis_limit * 100) if per_analysis_limit > 0 else 0
    
    return {
        "today_spent_usd": round(today_total, 4),
        "daily_limit_usd": daily_limit,
        "daily_usage_percent": round(daily_pct, 2),
        "daily_remaining_usd": round(max(0, daily_limit - today_total), 4),
        "max_track_cost_today_usd": round(max_track_cost, 4),
        "per_analysis_limit_usd": per_analysis_limit,
        "status": "ok" if daily_pct < 80 else "warning" if daily_pct < 100 else "over_budget",
        "tracks_analyzed_today": len(analyses),
    }


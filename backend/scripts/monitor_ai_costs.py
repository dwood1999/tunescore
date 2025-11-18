#!/usr/bin/env python3
"""
AI Cost Monitoring Script

Quick CLI tool to check AI API costs without hitting the API.
Run from backend directory: python scripts/monitor_ai_costs.py
"""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models import Analysis, Track, User


async def get_overall_stats(db: AsyncSession) -> dict:
    """Get overall AI cost statistics."""
    stmt = select(Analysis).where(Analysis.ai_costs.isnot(None))
    result = await db.execute(stmt)
    analyses = result.scalars().all()

    total_cost = 0.0
    costs_by_feature = {}
    costs_by_model = {}

    for analysis in analyses:
        if analysis.ai_costs:
            for feature, cost_data in analysis.ai_costs.items():
                if isinstance(cost_data, dict):
                    cost = cost_data.get("cost", 0.0)
                    model = cost_data.get("model", "unknown")
                elif isinstance(cost_data, (int, float)):
                    cost = float(cost_data)
                    model = "unknown"
                else:
                    continue

                total_cost += cost
                costs_by_feature[feature] = costs_by_feature.get(feature, 0.0) + cost
                costs_by_model[model] = costs_by_model.get(model, 0.0) + cost

    return {
        "total_cost": total_cost,
        "total_analyses": len(analyses),
        "avg_per_analysis": total_cost / len(analyses) if analyses else 0.0,
        "costs_by_feature": costs_by_feature,
        "costs_by_model": costs_by_model,
    }


async def get_user_stats(db: AsyncSession, limit: int = 10) -> list[dict]:
    """Get per-user cost statistics."""
    stmt = select(User).limit(100)
    result = await db.execute(stmt)
    users = result.scalars().all()

    user_stats = []

    for user in users:
        # Get user's analyses
        stmt = (
            select(Analysis)
            .join(Track, Track.id == Analysis.track_id)
            .where(Track.user_id == user.id)
            .where(Analysis.ai_costs.isnot(None))
        )
        result = await db.execute(stmt)
        analyses = result.scalars().all()

        if not analyses:
            continue

        total_cost = 0.0
        for analysis in analyses:
            if analysis.ai_costs:
                for feature, cost_data in analysis.ai_costs.items():
                    if isinstance(cost_data, dict):
                        cost = cost_data.get("cost", 0.0)
                    elif isinstance(cost_data, (int, float)):
                        cost = float(cost_data)
                    else:
                        continue
                    total_cost += cost

        user_stats.append({
            "user_id": user.id,
            "email": user.email,
            "tier": getattr(user, "tier", "free"),
            "total_cost": total_cost,
            "analyses_count": len(analyses),
            "avg_per_analysis": total_cost / len(analyses) if analyses else 0.0,
        })

    # Sort by total cost
    user_stats.sort(key=lambda x: x["total_cost"], reverse=True)
    return user_stats[:limit]


async def get_recent_activity(db: AsyncSession, days: int = 7) -> dict:
    """Get recent AI activity."""
    start_date = datetime.utcnow() - timedelta(days=days)

    stmt = (
        select(Analysis)
        .where(Analysis.created_at >= start_date)
        .where(Analysis.ai_costs.isnot(None))
    )
    result = await db.execute(stmt)
    analyses = result.scalars().all()

    daily_costs = {}
    for analysis in analyses:
        day_key = analysis.created_at.date().isoformat()
        day_cost = 0.0

        if analysis.ai_costs:
            for feature, cost_data in analysis.ai_costs.items():
                if isinstance(cost_data, dict):
                    cost = cost_data.get("cost", 0.0)
                elif isinstance(cost_data, (int, float)):
                    cost = float(cost_data)
                else:
                    continue
                day_cost += cost

        daily_costs[day_key] = daily_costs.get(day_key, 0.0) + day_cost

    return {
        "period_days": days,
        "total_analyses": len(analyses),
        "total_cost": sum(daily_costs.values()),
        "daily_breakdown": dict(sorted(daily_costs.items())),
    }


def print_header(title: str) -> None:
    """Print formatted header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


async def main():
    """Main monitoring function."""
    print("\n🔍 TuneScore AI Cost Monitoring Dashboard")
    print(f"   Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    async with AsyncSessionLocal() as db:
        # Overall Statistics
        print_header("Overall Statistics")
        overall = await get_overall_stats(db)
        print(f"  Total Cost:          ${overall['total_cost']:.4f}")
        print(f"  Total Analyses:      {overall['total_analyses']}")
        print(f"  Avg per Analysis:    ${overall['avg_per_analysis']:.4f}")

        # Cost by Feature
        print_header("Cost by Feature")
        if overall['costs_by_feature']:
            for feature, cost in sorted(
                overall['costs_by_feature'].items(),
                key=lambda x: x[1],
                reverse=True
            ):
                print(f"  {feature:30s} ${cost:8.4f}")
        else:
            print("  No AI costs recorded yet")

        # Cost by Model
        print_header("Cost by AI Model")
        if overall['costs_by_model']:
            for model, cost in sorted(
                overall['costs_by_model'].items(),
                key=lambda x: x[1],
                reverse=True
            ):
                print(f"  {model:40s} ${cost:8.4f}")
        else:
            print("  No model data recorded yet")

        # Top Users by Cost
        print_header("Top 10 Users by AI Spend")
        user_stats = await get_user_stats(db, limit=10)
        if user_stats:
            print(f"  {'User Email':35s} {'Tier':10s} {'Total Cost':>12s} {'Analyses':>10s}")
            print(f"  {'-' * 70}")
            for user in user_stats:
                print(
                    f"  {user['email']:35s} "
                    f"{user['tier']:10s} "
                    f"${user['total_cost']:>11.4f} "
                    f"{user['analyses_count']:>10d}"
                )
        else:
            print("  No user data yet")

        # Recent Activity
        print_header("Last 7 Days Activity")
        recent = await get_recent_activity(db, days=7)
        print(f"  Total Analyses:  {recent['total_analyses']}")
        print(f"  Total Cost:      ${recent['total_cost']:.4f}")
        print(f"\n  Daily Breakdown:")
        if recent['daily_breakdown']:
            for day, cost in sorted(recent['daily_breakdown'].items()):
                print(f"    {day}  ${cost:8.4f}")
        else:
            print("    No activity in last 7 days")

    print(f"\n{'=' * 70}\n")


if __name__ == "__main__":
    asyncio.run(main())


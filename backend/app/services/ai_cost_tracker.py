"""AI Cost Tracking Utilities."""

import logging
from datetime import datetime
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Analysis

logger = logging.getLogger(__name__)


class AICostTracker:
    """Track and record AI API costs for analyses."""

    @staticmethod
    async def record_cost(
        db: AsyncSession,
        analysis_id: int,
        feature: str,
        cost: float,
        model: str | None = None,
        tokens: dict[str, int] | None = None,
    ) -> None:
        """
        Record AI cost for a specific feature in an analysis.

        Args:
            db: Database session
            analysis_id: Analysis record ID
            feature: Feature name (e.g., 'pitch_generation', 'genre_classification')
            cost: Cost in USD
            model: AI model used (e.g., 'claude-3-5-sonnet-20241022')
            tokens: Token usage dict with 'input' and 'output' keys
        """
        try:
            # Fetch current analysis
            stmt = select(Analysis).where(Analysis.id == analysis_id)
            result = await db.execute(stmt)
            analysis = result.scalar_one_or_none()

            if not analysis:
                logger.error(f"Analysis {analysis_id} not found for cost tracking")
                return

            # Initialize or get existing costs
            ai_costs = analysis.ai_costs or {}

            # Record cost details
            cost_entry = {
                "cost": round(cost, 6),
                "timestamp": datetime.utcnow().isoformat(),
            }

            if model:
                cost_entry["model"] = model

            if tokens:
                cost_entry["tokens"] = tokens

            # Update the costs dict
            ai_costs[feature] = cost_entry

            # Update database
            stmt = (
                update(Analysis)
                .where(Analysis.id == analysis_id)
                .values(ai_costs=ai_costs)
            )
            await db.execute(stmt)
            await db.commit()

            logger.info(
                f"Recorded AI cost: ${cost:.4f} for feature '{feature}' "
                f"on analysis {analysis_id}"
            )

        except Exception as e:
            logger.error(f"Failed to record AI cost: {e}")
            await db.rollback()

    @staticmethod
    async def get_analysis_total_cost(
        db: AsyncSession, analysis_id: int
    ) -> float:
        """Get total AI cost for an analysis."""
        stmt = select(Analysis.ai_costs).where(Analysis.id == analysis_id)
        result = await db.execute(stmt)
        ai_costs = result.scalar_one_or_none()

        if not ai_costs:
            return 0.0

        total = 0.0
        for feature, cost_data in ai_costs.items():
            if isinstance(cost_data, dict):
                total += cost_data.get("cost", 0.0)
            elif isinstance(cost_data, (int, float)):
                total += float(cost_data)

        return round(total, 4)

    @staticmethod
    def calculate_anthropic_cost(
        input_tokens: int,
        output_tokens: int,
        model: str = "claude-3-5-sonnet-20241022",
    ) -> dict[str, Any]:
        """
        Calculate cost for Anthropic API usage.

        Pricing as of Nov 2024:
        - Claude 3.5 Sonnet: $3/MTok input, $15/MTok output
        - Claude 3 Haiku: $0.25/MTok input, $1.25/MTok output
        """
        pricing = {
            "claude-3-5-sonnet-20241022": {"input": 3.0, "output": 15.0},
            "claude-3-5-sonnet-20240620": {"input": 3.0, "output": 15.0},
            "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
            "claude-3-opus-20240229": {"input": 15.0, "output": 75.0},
        }

        rates = pricing.get(model, {"input": 3.0, "output": 15.0})

        input_cost = (input_tokens / 1_000_000) * rates["input"]
        output_cost = (output_tokens / 1_000_000) * rates["output"]
        total_cost = input_cost + output_cost

        return {
            "cost": round(total_cost, 6),
            "model": model,
            "tokens": {
                "input": input_tokens,
                "output": output_tokens,
                "total": input_tokens + output_tokens,
            },
            "breakdown": {
                "input_cost": round(input_cost, 6),
                "output_cost": round(output_cost, 6),
            },
        }

    @staticmethod
    def calculate_openai_cost(
        input_tokens: int,
        output_tokens: int,
        model: str = "gpt-4-turbo",
    ) -> dict[str, Any]:
        """
        Calculate cost for OpenAI API usage.

        Pricing as of Nov 2024:
        - GPT-4 Turbo: $10/MTok input, $30/MTok output
        - GPT-3.5 Turbo: $0.50/MTok input, $1.50/MTok output
        """
        pricing = {
            "gpt-4-turbo": {"input": 10.0, "output": 30.0},
            "gpt-4-turbo-preview": {"input": 10.0, "output": 30.0},
            "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
            "gpt-4": {"input": 30.0, "output": 60.0},
        }

        rates = pricing.get(model, {"input": 10.0, "output": 30.0})

        input_cost = (input_tokens / 1_000_000) * rates["input"]
        output_cost = (output_tokens / 1_000_000) * rates["output"]
        total_cost = input_cost + output_cost

        return {
            "cost": round(total_cost, 6),
            "model": model,
            "tokens": {
                "input": input_tokens,
                "output": output_tokens,
                "total": input_tokens + output_tokens,
            },
            "breakdown": {
                "input_cost": round(input_cost, 6),
                "output_cost": round(output_cost, 6),
            },
        }


# Convenience function for easy import
async def track_ai_cost(
    db: AsyncSession,
    analysis_id: int,
    feature: str,
    cost: float,
    model: str | None = None,
    tokens: dict[str, int] | None = None,
) -> None:
    """Convenience wrapper for tracking AI costs."""
    await AICostTracker.record_cost(
        db=db,
        analysis_id=analysis_id,
        feature=feature,
        cost=cost,
        model=model,
        tokens=tokens,
    )


"""Data aggregation and normalization helpers for Industry Pulse."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def normalize_chart_data(raw_data: dict[str, Any], platform: str) -> dict[str, Any]:
    """Normalize chart data from different platforms to common format.
    
    Args:
        raw_data: Platform-specific chart data
        platform: "spotify", "apple", "billboard", etc.
        
    Returns:
        Normalized chart entry
    """
    # Placeholder for future enhancement
    return raw_data


def calculate_velocity(
    current_position: int, previous_position: int | None
) -> dict[str, Any]:
    """Calculate chart velocity metrics.
    
    Args:
        current_position: Current chart position
        previous_position: Previous chart position (or None if new entry)
        
    Returns:
        Velocity metrics (movement, acceleration, etc.)
    """
    if previous_position is None:
        return {"movement": 0, "new_entry": True, "velocity_score": 0}

    movement = previous_position - current_position  # Positive = moving up
    velocity_score = abs(movement) * (100 - current_position)  # Weight by position

    return {
        "movement": movement,
        "new_entry": False,
        "velocity_score": velocity_score,
        "direction": "up" if movement > 0 else "down" if movement < 0 else "stable",
    }


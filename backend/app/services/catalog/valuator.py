"""Catalog valuation using DCF (Discounted Cash Flow) model.

Estimates catalog value based on historical revenue, growth rates, and industry multiples.
"""

import logging
from datetime import date
from typing import Any

logger = logging.getLogger(__name__)


class CatalogValuator:
    """
    Value music catalogs using DCF and market-based approaches.

    Industry standard: Catalogs typically sell for 10-20x annual royalties.
    Factors: growth rate, hit density, genre durability, cultural relevance.
    """

    # Industry multiples by genre (based on market data)
    GENRE_MULTIPLES = {
        "rock": 16.0,
        "pop": 15.0,
        "hip-hop": 14.0,
        "r&b": 15.5,
        "country": 17.0,  # More durable
        "electronic": 13.0,
        "jazz": 16.5,
        "classical": 18.0,  # Very durable
        "indie": 13.5,
        "metal": 14.5,
    }

    BASE_MULTIPLE = 15.0  # Default if genre not found

    def calculate_valuation(
        self,
        tracks: list[dict[str, Any]],
        revenue_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Calculate catalog valuation.

        Args:
            tracks: List of track data with metadata and metrics
            revenue_data: Optional historical revenue data

        Returns:
            Valuation breakdown
        """
        # Calculate annual revenue from tracks
        streaming_revenue = self._estimate_streaming_revenue(tracks)
        sync_revenue = self._estimate_sync_revenue(tracks)
        performance_revenue = self._estimate_performance_revenue(tracks)

        total_annual_revenue = streaming_revenue + sync_revenue + performance_revenue

        # Determine base multiple
        base_multiple = self._determine_base_multiple(tracks)

        # Adjust for growth rate
        growth_adjusted_multiple = self._adjust_for_growth(
            base_multiple, tracks, revenue_data
        )

        # Adjust for hit density
        hit_adjusted_multiple = self._adjust_for_hit_density(
            growth_adjusted_multiple, tracks
        )

        # Adjust for genre durability
        final_multiple = self._adjust_for_genre(hit_adjusted_multiple, tracks)

        # Calculate valuation
        estimated_value = total_annual_revenue * final_multiple

        # Calculate confidence based on data quality
        confidence = self._calculate_confidence(tracks, revenue_data)

        return {
            "estimated_value": round(estimated_value, 2),
            "annual_revenue": round(total_annual_revenue, 2),
            "valuation_multiple": round(final_multiple, 2),
            "base_multiple": round(base_multiple, 2),
            "confidence": round(confidence, 2),
            "revenue_breakdown": {
                "streaming": round(streaming_revenue, 2),
                "sync": round(sync_revenue, 2),
                "performance": round(performance_revenue, 2),
            },
            "valuation_factors": {
                "total_tracks": len(tracks),
                "hit_tracks": sum(
                    1 for t in tracks if t.get("tunescore", 0) > 75
                ),
                "avg_tunescore": round(
                    sum(t.get("tunescore", 0) for t in tracks) / len(tracks), 1
                )
                if tracks
                else 0,
            },
            "methodology": "DCF + Market Multiples",
            "valuation_date": date.today().isoformat(),
        }

    def _estimate_streaming_revenue(self, tracks: list[dict[str, Any]]) -> float:
        """
        Estimate annual streaming revenue.

        Industry average: $0.003-0.005 per stream across platforms.
        Using $0.004 as middle estimate.
        """
        REVENUE_PER_STREAM = 0.004

        total_annual_streams = 0
        for track in tracks:
            # Estimate annual streams from monthly or total streams
            monthly_streams = track.get("monthly_streams", 0)
            if monthly_streams:
                total_annual_streams += monthly_streams * 12
            else:
                # Fallback: use total streams and assume 20% annual decay
                total_streams = track.get("total_streams", 0)
                total_annual_streams += total_streams * 0.20

        return total_annual_streams * REVENUE_PER_STREAM

    def _estimate_sync_revenue(self, tracks: list[dict[str, Any]]) -> float:
        """
        Estimate annual sync licensing revenue.

        Based on:
        - Number of tracks with sync-ready tags
        - Production quality
        - Genre suitability
        """
        sync_ready_tracks = 0
        for track in tracks:
            tags = track.get("commercial_tags", [])
            if "sync-ready" in tags or "instrumental-friendly" in tags:
                sync_ready_tracks += 1

        # Average sync deal: $2,000-$50,000
        # Conservative estimate: $5,000 per sync-ready track per year
        # Assume 10% placement rate
        avg_sync_value = 5000
        placement_rate = 0.10

        return sync_ready_tracks * avg_sync_value * placement_rate

    def _estimate_performance_revenue(self, tracks: list[dict[str, Any]]) -> float:
        """
        Estimate performance royalties (radio, live, etc.).

        Based on streaming popularity as proxy for radio play.
        """
        # Performance royalties typically 10-15% of streaming revenue
        streaming_revenue = self._estimate_streaming_revenue(tracks)
        return streaming_revenue * 0.12

    def _determine_base_multiple(self, tracks: list[dict[str, Any]]) -> float:
        """Determine base multiple from genre distribution."""
        if not tracks:
            return self.BASE_MULTIPLE

        # Get genre distribution
        genre_counts = {}
        for track in tracks:
            genre = track.get("genre", "").lower()
            if genre:
                genre_counts[genre] = genre_counts.get(genre, 0) + 1

        if not genre_counts:
            return self.BASE_MULTIPLE

        # Weighted average of genre multiples
        total_tracks = len(tracks)
        weighted_multiple = 0

        for genre, count in genre_counts.items():
            weight = count / total_tracks
            multiple = self.GENRE_MULTIPLES.get(genre, self.BASE_MULTIPLE)
            weighted_multiple += multiple * weight

        return weighted_multiple

    def _adjust_for_growth(
        self,
        base_multiple: float,
        tracks: list[dict[str, Any]],
        revenue_data: dict[str, Any] | None,
    ) -> float:
        """Adjust multiple based on growth rate."""
        if not revenue_data:
            return base_multiple

        growth_rate = revenue_data.get("yoy_growth_rate", 0)

        # Positive growth increases multiple
        if growth_rate > 0.15:  # >15% YoY growth
            return base_multiple + 3.0
        elif growth_rate > 0.10:  # >10% YoY growth
            return base_multiple + 2.0
        elif growth_rate > 0.05:  # >5% YoY growth
            return base_multiple + 1.0
        elif growth_rate < -0.05:  # Declining >5%
            return base_multiple - 2.0
        elif growth_rate < -0.10:  # Declining >10%
            return base_multiple - 3.0

        return base_multiple

    def _adjust_for_hit_density(
        self, base_multiple: float, tracks: list[dict[str, Any]]
    ) -> float:
        """Adjust for percentage of high-quality tracks."""
        if not tracks:
            return base_multiple

        # Count tracks with tunescore > 75
        hit_tracks = sum(1 for t in tracks if t.get("tunescore", 0) > 75)
        hit_density = hit_tracks / len(tracks)

        # High hit density = premium
        if hit_density > 0.30:  # >30% hits
            return base_multiple + 2.5
        elif hit_density > 0.20:  # >20% hits
            return base_multiple + 1.5
        elif hit_density > 0.10:  # >10% hits
            return base_multiple + 0.5
        elif hit_density < 0.05:  # <5% hits
            return base_multiple - 1.0

        return base_multiple

    def _adjust_for_genre(
        self, base_multiple: float, tracks: list[dict[str, Any]]
    ) -> float:
        """Final adjustment already incorporated in base multiple."""
        # Genre is already factored into base_multiple
        # This is a placeholder for additional genre-specific factors
        return base_multiple

    def _calculate_confidence(
        self, tracks: list[dict[str, Any]], revenue_data: dict[str, Any] | None
    ) -> float:
        """
        Calculate confidence score for valuation (0-1).

        Higher confidence when:
        - More tracks in catalog
        - Actual revenue data available
        - Recent streaming data
        - Complete metadata
        """
        confidence = 0.5  # Base confidence

        # More tracks = higher confidence
        if len(tracks) > 50:
            confidence += 0.15
        elif len(tracks) > 20:
            confidence += 0.10
        elif len(tracks) > 10:
            confidence += 0.05

        # Actual revenue data
        if revenue_data:
            confidence += 0.20

        # Data completeness
        complete_tracks = sum(
            1
            for t in tracks
            if t.get("monthly_streams")
            and t.get("tunescore")
            and t.get("genre")
        )
        if tracks:
            completeness = complete_tracks / len(tracks)
            confidence += completeness * 0.15

        return min(1.0, confidence)


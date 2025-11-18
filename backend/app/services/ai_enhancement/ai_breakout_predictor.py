"""AI-powered breakout prediction with strategic insights."""

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class AIBreakoutPredictor:
    """Predict breakout potential with AI-powered strategic insights."""

    MAX_COST_PER_REQUEST = 0.008

    def __init__(self) -> None:
        """Initialize with available API."""
        self.provider = None
        self.client = None
        self.model = ""

        # DeepSeek first
        if os.getenv("DEEPSEEK_API_KEY"):
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=os.getenv("DEEPSEEK_API_KEY"),
                    base_url="https://api.deepseek.com/v1"
                )
                self.model = "deepseek-chat"
                self.provider = "deepseek"
            except Exception as e:
                logger.warning(f"Failed to init DeepSeek: {e}")

        if not self.client and os.getenv("ANTHROPIC_API_KEY"):
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
                self.model = "claude-3-haiku-20240307"
                self.provider = "anthropic"
            except Exception as e:
                logger.warning(f"Failed to init Anthropic: {e}")

        if not self.client and os.getenv("OPENAI_API_KEY"):
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                self.model = "gpt-4o-mini"
                self.provider = "openai"
            except Exception as e:
                logger.warning(f"Failed to init OpenAI: {e}")

    def predict_breakout(
        self,
        track_title: str,
        artist_name: str,
        tunescore: dict[str, Any],
        genre: str,
        moods: list[str],
        hook_strength: float,
        track_duration: float = None
    ) -> dict[str, Any] | None:
        """
        Predict breakout potential with strategic insights.
        
        Args:
            track_title: Track title
            artist_name: Artist name
            tunescore: TuneScore data
            genre: Primary genre
            moods: Mood tags
            hook_strength: Hook catchiness (0-1)
            track_duration: Track length in seconds
        
        Returns:
            Breakout prediction with strategic advice
        """
        if not self.client:
            return None

        try:
            overall_score = tunescore.get("overall_score", 50)
            duration_str = f"{track_duration // 60:.0f}:{track_duration % 60:02.0f}" if track_duration else "Unknown"
            moods_str = ", ".join(moods[:5]) if moods else "Unknown"
            
            prompt = f"""You are a music industry A&R expert and trend analyst. Predict this track's breakout potential.

**Track:** "{track_title}" by {artist_name}
**Genre:** {genre}
**TuneScore:** {overall_score}/100
**Hook Strength:** {hook_strength:.2f}
**Duration:** {duration_str}
**Moods:** {moods_str}

**Task:** Analyze breakout potential considering current music trends (TikTok, streaming, radio, sync).

Return JSON:
{{
  "breakout_score": 7.5,
  "breakout_explanation": "Why this track has/lacks breakout potential",
  "tiktok_potential": {{
    "score": 8.0,
    "reasoning": "Why this works/doesn't work for TikTok",
    "memeable_moments": ["Timestamp 1", "Timestamp 2"],
    "trend_alignment": "How it fits current TikTok trends"
  }},
  "radio_potential": {{
    "score": 6.5,
    "reasoning": "Radio-friendliness assessment",
    "concerns": ["Duration too long", "Hook comes late"]
  }},
  "streaming_potential": {{
    "score": 8.5,
    "playlist_targets": ["Playlist 1", "Playlist 2"],
    "skip_rate_prediction": "low/medium/high"
  }},
  "sync_licensing_value": {{
    "score": 7.0,
    "target_brands": ["Brand 1", "Brand 2"],
    "estimated_deal_range": "$10K-$30K"
  }},
  "strategic_recommendations": [
    "Release in summer for maximum impact",
    "Create radio edit at 3:15",
    "Target Spotify's 'Pop Rising' playlist"
  ],
  "comparable_breakout_tracks": [
    {{"artist": "Artist X", "track": "Track Y", "trajectory": "Went viral on TikTok, 100M streams"}}
  ]
}}

Be data-driven but creative. Consider current music industry trends. Return ONLY valid JSON."""

            # Call AI
            if self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1200,
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}],
                )
                response_text = response.content[0].text
                cost = (response.usage.input_tokens / 1_000_000) * 0.25 + \
                       (response.usage.output_tokens / 1_000_000) * 1.25
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=1200,
                )
                response_text = response.choices[0].message.content
                if self.provider == "deepseek":
                    cost = (response.usage.prompt_tokens / 1_000_000) * 0.14 + \
                           (response.usage.completion_tokens / 1_000_000) * 0.28
                else:
                    cost = (response.usage.prompt_tokens / 1_000_000) * 0.15 + \
                           (response.usage.completion_tokens / 1_000_000) * 0.60
            
            result = self._parse_response(response_text)
            result["cost"] = round(cost, 4)
            result["provider"] = self.provider
            
            logger.info(f"AI breakout prediction complete: ${cost:.4f}")
            return result
            
        except Exception as e:
            logger.error(f"AI breakout prediction failed: {e}")
            return None

    def _parse_response(self, response_text: str) -> dict[str, Any]:
        """Parse AI response."""
        try:
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse breakout prediction: {e}")
            return {"error": "Failed to parse response"}


def predict_breakout_with_ai(
    track_title: str,
    artist_name: str,
    tunescore: dict[str, Any],
    genre: str,
    moods: list[str],
    hook_strength: float,
    track_duration: float = None
) -> dict[str, Any] | None:
    """Convenience function."""
    try:
        predictor = AIBreakoutPredictor()
        return predictor.predict_breakout(
            track_title, artist_name, tunescore, genre, moods, hook_strength, track_duration
        )
    except Exception as e:
        logger.error(f"AI breakout prediction failed: {e}")
        return None


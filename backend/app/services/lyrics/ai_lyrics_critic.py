"""AI-powered lyrics critique using LLM."""

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class AILyricsCritic:
    """AI-powered lyrics critique with multi-provider support."""

    MAX_COST_PER_REQUEST = 0.01  # Cost governor: max $0.01 per critique

    def __init__(self) -> None:
        """Initialize lyrics critic with available API."""
        self.provider = None
        self.client = None
        self.model = ""

        # Try DeepSeek first (cheapest!)
        if os.getenv("DEEPSEEK_API_KEY"):
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=os.getenv("DEEPSEEK_API_KEY"),
                    base_url="https://api.deepseek.com/v1"
                )
                self.model = "deepseek-chat"
                self.provider = "deepseek"
                logger.info("✅ Lyrics critic using DeepSeek Chat")
            except Exception as e:
                logger.warning(f"Failed to init DeepSeek: {e}")

        # Fallback to Anthropic
        if not self.client and os.getenv("ANTHROPIC_API_KEY"):
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
                self.model = "claude-3-haiku-20240307"
                self.provider = "anthropic"
                logger.info("✅ Lyrics critic using Anthropic Claude 3 Haiku")
            except Exception as e:
                logger.warning(f"Failed to init Anthropic: {e}")

        # Fallback to OpenAI
        if not self.client and os.getenv("OPENAI_API_KEY"):
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                self.model = "gpt-4o-mini"
                self.provider = "openai"
                logger.info("✅ Lyrics critic using OpenAI GPT-4o Mini")
            except Exception as e:
                logger.warning(f"Failed to init OpenAI: {e}")

    def critique_lyrics(
        self,
        lyrics: str,
        track_title: str = "",
        artist_name: str = "",
        sections: list[dict[str, Any]] = None,
        themes: list[str] = None,
        sentiment: dict[str, Any] = None
    ) -> dict[str, Any] | None:
        """
        Generate AI-powered lyrics critique.
        
        Args:
            lyrics: Full lyrics text
            track_title: Track title for context
            artist_name: Artist name for context
            sections: Detected sections (verse, chorus, etc.)
            themes: Extracted themes
            sentiment: Sentiment analysis data
        
        Returns:
            Dictionary with critique and ratings, or None if unavailable
        """
        if not self.client:
            logger.warning("No AI provider available - skipping lyrics critique")
            return None

        try:
            # Build prompt
            prompt = self._build_prompt(
                lyrics, track_title, artist_name, sections, themes, sentiment
            )
            
            # Call AI
            if self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    temperature=0.5,
                    messages=[{"role": "user", "content": prompt}],
                )
                response_text = response.content[0].text
                # Calculate cost
                cost = self._calculate_cost_anthropic(
                    response.usage.input_tokens,
                    response.usage.output_tokens
                )
            else:  # OpenAI or DeepSeek
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5,
                    max_tokens=2000,
                )
                response_text = response.choices[0].message.content
                # Calculate cost
                cost = self._calculate_cost_openai(
                    response.usage.prompt_tokens,
                    response.usage.completion_tokens
                )
            
            # Check cost governor
            if cost > self.MAX_COST_PER_REQUEST:
                logger.warning(
                    f"Lyrics critique cost ${cost:.4f} exceeds max ${self.MAX_COST_PER_REQUEST}"
                )
            
            # Parse JSON response
            result = self._parse_response(response_text)
            result["cost"] = round(cost, 4)
            result["provider"] = self.provider
            
            logger.info(f"AI lyrics critique complete: ${cost:.4f} cost")
            
            return result
            
        except Exception as e:
            logger.error(f"AI lyrics critique failed: {e}")
            return None

    def _build_prompt(
        self,
        lyrics: str,
        track_title: str,
        artist_name: str,
        sections: list[dict[str, Any]],
        themes: list[str],
        sentiment: dict[str, Any]
    ) -> str:
        """Build prompt for AI lyrics critique."""
        context = ""
        if track_title:
            context += f"Song: \"{track_title}\""
        if artist_name:
            context += f" by {artist_name}"
        
        structure_info = ""
        if sections:
            section_types = [s["type"] for s in sections]
            structure_info = f"\n\nDetected Structure: {' -> '.join(section_types)}"
        
        themes_info = ""
        if themes:
            themes_info = f"\n\nDetected Themes: {', '.join(themes[:5])}"
        
        sentiment_info = ""
        if sentiment and "compound" in sentiment:
            sentiment_label = "positive" if sentiment["compound"] > 0.1 else "negative" if sentiment["compound"] < -0.1 else "neutral"
            sentiment_info = f"\n\nOverall Sentiment: {sentiment_label}"
        
        return f"""You are an expert songwriting coach and A&R consultant. Analyze the following song lyrics and provide constructive, actionable feedback.

{context}{structure_info}{themes_info}{sentiment_info}

LYRICS:
{lyrics}

TASK:
Provide a comprehensive critique with the following:

1. **Strengths** (2-3 specific examples of what works well)
2. **Weaknesses** (2-3 specific areas for improvement)
3. **Imagery & Metaphors** (Are they vivid? Original? Clichéd?)
4. **Emotional Impact** (Does it connect emotionally? Where does it peak?)
5. **Commercial Potential** (Sync licensing, radio-friendly, memorable hooks?)
6. **Actionable Suggestions** (2-3 concrete ways to improve the song)

Return a JSON object with this EXACT structure:
{{
  "overall_rating": 8.2,
  "overall_summary": "Brief 1-2 sentence summary of the song's quality",
  "strengths": [
    "Specific strength 1",
    "Specific strength 2"
  ],
  "weaknesses": [
    "Specific weakness 1",
    "Specific weakness 2"
  ],
  "imagery_rating": 7.5,
  "imagery_feedback": "Assessment of imagery and metaphors",
  "emotional_impact_rating": 8.0,
  "emotional_peak": "Where the song's emotional peak occurs",
  "commercial_potential_rating": 7.0,
  "commercial_feedback": "Assessment of commercial viability",
  "target_audience": "Who this song is for",
  "sync_opportunities": ["Film/TV opportunity 1", "Film/TV opportunity 2"],
  "actionable_suggestions": [
    "Concrete suggestion 1",
    "Concrete suggestion 2"
  ],
  "comparable_artists": ["Artist 1", "Artist 2", "Artist 3"]
}}

IMPORTANT: 
- Be constructive, not harsh
- Provide specific examples from the lyrics
- Rate on a scale of 0-10 (decimals OK)
- Return ONLY valid JSON, no additional text
- Focus on what the artist can DO to improve"""

    def _parse_response(self, response_text: str) -> dict[str, Any]:
        """Parse AI response and extract JSON."""
        try:
            # Try to find JSON in response (handles cases where AI adds explanation)
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            result = json.loads(response_text)
            
            # Validate structure
            required_fields = ["overall_rating", "overall_summary", "strengths", "weaknesses"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.debug(f"Response text: {response_text[:500]}")
            return {"error": "Failed to parse AI response"}

    def _calculate_cost_anthropic(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for Anthropic Claude."""
        # Claude 3 Haiku pricing: $0.25/MTok input, $1.25/MTok output
        input_cost = (input_tokens / 1_000_000) * 0.25
        output_cost = (output_tokens / 1_000_000) * 1.25
        return input_cost + output_cost

    def _calculate_cost_openai(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for OpenAI or DeepSeek."""
        if self.provider == "deepseek":
            # DeepSeek pricing: $0.14/MTok input, $0.28/MTok output
            input_cost = (input_tokens / 1_000_000) * 0.14
            output_cost = (output_tokens / 1_000_000) * 0.28
        else:  # OpenAI GPT-4o-mini
            # GPT-4o-mini pricing: $0.15/MTok input, $0.60/MTok output
            input_cost = (input_tokens / 1_000_000) * 0.15
            output_cost = (output_tokens / 1_000_000) * 0.60
        return input_cost + output_cost


def critique_lyrics_with_ai(
    lyrics: str,
    track_title: str = "",
    artist_name: str = "",
    sections: list[dict[str, Any]] = None,
    themes: list[str] = None,
    sentiment: dict[str, Any] = None
) -> dict[str, Any] | None:
    """
    Convenience function to critique lyrics with AI.
    
    Returns None if AI is not available.
    """
    try:
        critic = AILyricsCritic()
        return critic.critique_lyrics(
            lyrics, track_title, artist_name, sections, themes, sentiment
        )
    except Exception as e:
        logger.error(f"AI lyrics critique failed: {e}")
        return None



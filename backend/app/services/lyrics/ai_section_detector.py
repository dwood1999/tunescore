"""AI-powered song section detection using LLM."""

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class AISectionDetector:
    """AI-powered song section detection with multi-provider support."""

    MAX_COST_PER_REQUEST = 0.02  # Cost governor: max $0.02 per analysis

    def __init__(self) -> None:
        """Initialize section detector with available API."""
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
                logger.info("✅ Section detector using DeepSeek Chat (ultra cheap!)")
            except Exception as e:
                logger.warning(f"Failed to init DeepSeek: {e}")

        # Fallback to Anthropic
        if not self.client and os.getenv("ANTHROPIC_API_KEY"):
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
                self.model = "claude-3-haiku-20240307"
                self.provider = "anthropic"
                logger.info("✅ Section detector using Anthropic Claude 3 Haiku")
            except Exception as e:
                logger.warning(f"Failed to init Anthropic: {e}")

        # Fallback to OpenAI
        if not self.client and os.getenv("OPENAI_API_KEY"):
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                self.model = "gpt-4o-mini"
                self.provider = "openai"
                logger.info("✅ Section detector using OpenAI GPT-4o Mini")
            except Exception as e:
                logger.warning(f"Failed to init OpenAI: {e}")

    def detect_sections(self, lyrics: str, track_title: str = "", artist_name: str = "") -> dict[str, Any]:
        """
        Use AI to detect song sections accurately.
        
        Args:
            lyrics: Full lyrics text
            track_title: Track title for context
            artist_name: Artist name for context
        
        Returns:
            Dictionary with sections list and structure pattern
        """
        if not self.client:
            logger.warning("No AI provider available - using fallback heuristic detection")
            return None  # Will fall back to heuristic method

        try:
            # Build prompt
            prompt = self._build_prompt(lyrics, track_title, artist_name)
            
            # Call AI
            if self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1500,
                    temperature=0.3,  # Low temperature for consistent structure detection
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
                    temperature=0.3,
                    max_tokens=1500,
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
                    f"Section detection cost ${cost:.4f} exceeds max ${self.MAX_COST_PER_REQUEST}"
                )
            
            # Parse JSON response
            result = self._parse_response(response_text)
            result["cost"] = round(cost, 4)
            result["provider"] = self.provider
            
            logger.info(
                f"AI section detection complete: {len(result.get('sections', []))} sections, "
                f"${cost:.4f} cost"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"AI section detection failed: {e}")
            return None  # Fall back to heuristic

    def _build_prompt(self, lyrics: str, track_title: str, artist_name: str) -> str:
        """Build prompt for AI section detection."""
        context = ""
        if track_title:
            context += f"Song: \"{track_title}\""
        if artist_name:
            context += f" by {artist_name}"
        
        return f"""Analyze the following song lyrics and identify the song sections (verse, chorus, bridge, pre-chorus, outro, intro, etc.).

{context}

LYRICS:
{lyrics}

TASK:
1. Identify each distinct section in the song
2. Label each section correctly (verse 1, verse 2, chorus, bridge, etc.)
3. For narrative songs, verses should be numbered sequentially (1, 2, 3, etc.)
4. Choruses are repeated sections with the same or very similar lyrics
5. Bridges are unique sections that differ from verses and choruses
6. Pre-choruses come before choruses and build tension

Return a JSON object with this EXACT structure:
{{
  "sections": [
    {{
      "type": "verse 1",
      "content": "lyrics text here",
      "line_count": 4
    }},
    {{
      "type": "chorus",
      "content": "chorus lyrics here",
      "line_count": 4
    }}
  ],
  "structure_pattern": "verse 1 -> chorus -> verse 2 -> chorus -> bridge -> chorus",
  "has_bridge": true,
  "has_pre_chorus": false,
  "total_sections": 5,
  "section_counts": {{
    "verse": 2,
    "chorus": 3,
    "bridge": 1
  }}
}}

IMPORTANT: Return ONLY valid JSON, no additional text."""

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
            if "sections" not in result or not isinstance(result["sections"], list):
                raise ValueError("Invalid response structure: missing 'sections' array")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.debug(f"Response text: {response_text[:500]}")
            return {"error": "Failed to parse AI response", "sections": []}

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


def analyze_sections_with_ai(
    lyrics: str, 
    track_title: str = "", 
    artist_name: str = ""
) -> dict[str, Any] | None:
    """
    Convenience function to analyze sections with AI.
    
    Returns None if AI is not available (will fall back to heuristic).
    """
    try:
        detector = AISectionDetector()
        return detector.detect_sections(lyrics, track_title, artist_name)
    except Exception as e:
        logger.error(f"AI section analysis failed: {e}")
        return None



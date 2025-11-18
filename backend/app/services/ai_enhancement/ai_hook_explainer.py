"""AI-powered hook explanation with commercial context."""

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class AIHookExplainer:
    """Explain WHY hooks are catchy and their commercial potential."""

    MAX_COST_PER_REQUEST = 0.005

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

        # Fallback to Anthropic
        if not self.client and os.getenv("ANTHROPIC_API_KEY"):
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
                self.model = "claude-3-haiku-20240307"
                self.provider = "anthropic"
            except Exception as e:
                logger.warning(f"Failed to init Anthropic: {e}")

        # Fallback to OpenAI
        if not self.client and os.getenv("OPENAI_API_KEY"):
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                self.model = "gpt-4o-mini"
                self.provider = "openai"
            except Exception as e:
                logger.warning(f"Failed to init OpenAI: {e}")

    def explain_hooks(
        self,
        track_title: str,
        hook_data: dict[str, Any],
        lyrical_sections: list[dict[str, Any]] = None,
        sonic_genome: dict[str, Any] = None
    ) -> dict[str, Any] | None:
        """
        Explain hook catchiness and commercial potential.
        
        Args:
            track_title: Track title
            hook_data: Hook analysis data
            lyrical_sections: Song sections
            sonic_genome: Sonic features
        
        Returns:
            Dictionary with hook explanations
        """
        if not self.client or not hook_data:
            return None

        try:
            # Extract hook info
            hook_timestamp = hook_data.get("hook_timestamp", "Unknown")
            hook_strength = hook_data.get("hook_strength", 0.5)
            
            # Get chorus section if available
            chorus_lyrics = ""
            if lyrical_sections:
                choruses = [s for s in lyrical_sections if "chorus" in s.get("type", "").lower()]
                if choruses:
                    chorus_lyrics = choruses[0].get("content", "")[:200]  # First 200 chars
            
            # Get energy/valence
            energy = sonic_genome.get("energy", 0.5) if sonic_genome else 0.5
            valence = sonic_genome.get("valence", 0.5) if sonic_genome else 0.5
            
            prompt = f"""You are a music producer and A&R expert. Explain WHY this track's hook is catchy and its commercial potential.

**Track:** "{track_title}"
**Hook Timestamp:** {hook_timestamp}
**Hook Strength:** {hook_strength:.2f} (0=weak, 1=strong)
**Energy:** {energy:.2f}
**Valence:** {valence:.2f}
**Chorus Lyrics:** {chorus_lyrics or "Not available"}

**Task:** Explain what makes this hook catchy and commercially viable.

Return JSON:
{{
  "hook_explanation": "Why is this hook catchy? What makes it memorable?",
  "commercial_appeal": "Why would this hook work for radio/streaming/sync?",
  "emotional_impact": "What emotion does the hook evoke?",
  "memorability_factors": ["Factor 1", "Factor 2"],
  "sync_licensing_potential": "Film/TV/ad suitability (e.g., sports montages, car commercials)",
  "tiktok_snippet_timestamp": "Ideal 15-second TikTok snippet timing",
  "radio_friendliness": 8.5,
  "earworm_rating": 7.0
}}

Return ONLY valid JSON."""

            # Call AI
            if self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=600,
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
                    max_tokens=600,
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
            
            logger.info(f"AI hook explanation complete: ${cost:.4f}")
            return result
            
        except Exception as e:
            logger.error(f"AI hook explanation failed: {e}")
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
            logger.error(f"Failed to parse hook explanation: {e}")
            return {"error": "Failed to parse response"}


def explain_hooks_with_ai(
    track_title: str,
    hook_data: dict[str, Any],
    lyrical_sections: list[dict[str, Any]] = None,
    sonic_genome: dict[str, Any] = None
) -> dict[str, Any] | None:
    """Convenience function."""
    try:
        explainer = AIHookExplainer()
        return explainer.explain_hooks(track_title, hook_data, lyrical_sections, sonic_genome)
    except Exception as e:
        logger.error(f"AI hook explanation failed: {e}")
        return None


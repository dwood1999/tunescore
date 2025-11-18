"""AI-powered pitch copy generation using Claude or OpenAI API.

Generates marketing copy for tracks with multiple AI provider fallbacks.
"""

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class PitchGenerator:
    """AI-powered pitch copy generation with multi-provider support."""

    MAX_COST_PER_REQUEST = 0.05  # Cost governor: max $0.05 per pitch

    def __init__(self) -> None:
        """Initialize pitch generator with available API.
        
        Priority order (best value to best quality):
        1. GPT-4o Mini (best value, excellent quality)
        2. Claude 3.5 Sonnet (best quality, premium)
        3. DeepSeek Chat (fallback, cheapest)
        """
        self.provider = None
        self.client = None
        self.model = ""

        # Try OpenAI GPT-4o Mini first (best value)
        if os.getenv("OPENAI_API_KEY"):
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                self.model = "gpt-4o-mini"
                self.provider = "openai"
                logger.info("✅ Pitch generator using OpenAI GPT-4o Mini (best value)")
            except Exception as e:
                logger.warning(f"Failed to init OpenAI: {e}")

        # Fallback to Claude 3.5 Sonnet (best quality)
        if not self.client and os.getenv("ANTHROPIC_API_KEY"):
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
                self.model = "claude-3-5-sonnet-20241022"
                self.provider = "anthropic"
                logger.info("✅ Pitch generator using Claude 3.5 Sonnet (best quality)")
            except Exception as e:
                logger.warning(f"Failed to init Anthropic: {e}")

        # Fallback to DeepSeek (cheapest option)
        if not self.client and os.getenv("DEEPSEEK_API_KEY"):
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=os.getenv("DEEPSEEK_API_KEY"),
                    base_url="https://api.deepseek.com/v1"
                )
                self.model = "deepseek-chat"
                self.provider = "deepseek"
                logger.info("✅ Pitch generator using DeepSeek Chat (fallback)")
            except Exception as e:
                logger.warning(f"Failed to init DeepSeek: {e}")

        if not self.client:
            raise ValueError("No AI API key available (tried OpenAI, Anthropic, DeepSeek)")

    def generate_pitch(
        self,
        track_title: str,
        artist_name: str,
        sonic_genome: dict[str, Any],
        lyrical_genome: dict[str, Any] | None,
        tags: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """
        Generate pitch copy for a track.

        Args:
            track_title: Track title
            artist_name: Artist name
            sonic_genome: Sonic analysis data
            lyrical_genome: Lyrical analysis data (optional)
            tags: Track tags (moods, commercial tags, etc.)

        Returns:
            Dictionary with pitch copy and cost
        """
        try:
            # Build prompt
            prompt = self._build_prompt(
                track_title, artist_name, sonic_genome, lyrical_genome, tags
            )

            # Call appropriate API based on provider
            if self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1500,
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}],
                )
                input_tokens = response.usage.input_tokens
                output_tokens = response.usage.output_tokens
                response_text = response.content[0].text

            elif self.provider in ["openai", "deepseek"]:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1500,
                    temperature=0.7,
                )
                input_tokens = response.usage.prompt_tokens
                output_tokens = response.usage.completion_tokens
                response_text = response.choices[0].message.content

            else:
                raise ValueError(f"Unknown provider: {self.provider}")

            # Calculate cost
            cost = self._calculate_cost(input_tokens, output_tokens)

            # Check cost governor
            if cost > self.MAX_COST_PER_REQUEST:
                logger.warning(
                    f"Pitch generation cost ${cost:.4f} exceeds max ${self.MAX_COST_PER_REQUEST}"
                )

            # Parse response
            pitch_data = self._parse_response(response_text)
            pitch_data["cost"] = round(cost, 4)
            pitch_data["provider"] = self.provider
            pitch_data["model"] = self.model
            pitch_data["tokens"] = {
                "input": input_tokens,
                "output": output_tokens,
                "total": input_tokens + output_tokens,
            }

            # Log to prompts log
            self._log_prompt(track_title, artist_name, pitch_data, cost)

            return pitch_data

        except Exception as e:
            logger.error(f"Pitch generation failed: {e}")
            return {
                "error": str(e),
                "elevator_pitch": "Track pitch generation temporarily unavailable.",
                "short_description": "",
                "sync_pitch": "",
                "cost": 0.0,
            }

    def _build_prompt(
        self,
        track_title: str,
        artist_name: str,
        sonic_genome: dict[str, Any],
        lyrical_genome: dict[str, Any] | None,
        tags: dict[str, Any] | None,
    ) -> str:
        """Build prompt for Claude."""
        # Extract key features
        tempo = sonic_genome.get("tempo", 0)
        energy = sonic_genome.get("energy", 0)
        valence = sonic_genome.get("valence", 0)
        genre = sonic_genome.get("genre", "Unknown")

        moods = tags.get("moods", []) if tags else []
        commercial_tags = tags.get("commercial_tags", []) if tags else []
        sounds_like = tags.get("sounds_like", []) if tags else []

        # Lyrical info
        themes = []
        if lyrical_genome:
            themes = lyrical_genome.get("themes_advanced", {})
            if isinstance(themes, dict):
                themes = list(themes.keys())[:3]

        prompt = f"""You are a music industry A&R professional and marketing copywriter. Generate compelling pitch copy for this track.

**Track Details:**
- Title: "{track_title}"
- Artist: {artist_name}

**Musical Analysis:**
- Genre: {genre}
- Tempo: {tempo:.0f} BPM
- Energy Level: {energy:.2f} (0-1 scale, higher = more energetic)
- Mood/Vibe: {valence:.2f} (0-1 scale, higher = more positive)
- Mood Tags: {", ".join(moods) if moods else "N/A"}
- Commercial Tags: {", ".join(commercial_tags) if commercial_tags else "N/A"}
"""

        if sounds_like:
            prompt += f"- Sounds Like: {', '.join(sounds_like)}\n"

        if themes:
            prompt += f"- Lyrical Themes: {', '.join(themes)}\n"

        prompt += """
**Task:**
Generate three types of pitch copy:

1. **Elevator Pitch** (1 sentence, max 25 words):
   - Concise, punchy description perfect for a quick pitch
   - Focus on the most compelling aspect (sound, vibe, or hook)
   - Example: "Sun-soaked indie-pop with infectious melodies and festival-ready energy"

2. **EPK Description** (2-3 sentences, ~50 words):
   - Expands on the elevator pitch
   - Highlight production quality, artistic vision, or unique elements
   - Mention comparable artists if relevant
   - Example: "This track blends the dreamy production of Tame Impala with the vocal urgency of The 1975. Perfect for late-night drives or pre-game playlists, it showcases [artist]'s evolution into a more polished, radio-ready sound."

3. **Sync Licensing Pitch** (2-3 sentences, ~50 words):
   - Focus on visual/emotional applications
   - Suggest specific use cases (film scenes, commercials, etc.)
   - Emphasize production elements that work well in media
   - Example: "Ideal for: Coming-of-age film montages, luxury car commercials, or reflective road trip scenes. The clean production and uplifting arc make it perfect for emotional storytelling without overpowering dialogue."

**Instructions:**
- Write in professional, industry-standard language
- Be specific about sound and production quality
- Avoid clichés like "game-changing" or "revolutionary"
- Focus on commercial potential and use cases
- Keep it authentic and grounded

**Output Format:**
Return ONLY a JSON object with these exact keys:
```json
{
  "elevator_pitch": "...",
  "short_description": "...",
  "sync_pitch": "..."
}
```

Do not include any other text outside the JSON.
"""

        return prompt

    def _parse_response(self, response_text: str) -> dict[str, str]:
        """Parse Claude's response into structured data."""
        try:
            # Try to extract JSON from response
            # Claude might wrap it in markdown code blocks
            response_text = response_text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            response_text = response_text.strip()

            # Parse JSON
            parsed = json.loads(response_text)

            return {
                "elevator_pitch": parsed.get("elevator_pitch", ""),
                "short_description": parsed.get("short_description", ""),
                "sync_pitch": parsed.get("sync_pitch", ""),
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse pitch JSON: {e}")
            # Fallback: try to extract sections manually
            return {
                "elevator_pitch": "Error parsing pitch",
                "short_description": response_text[:200] if len(response_text) > 200 else response_text,
                "sync_pitch": "",
            }

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on provider and model."""
        if self.provider == "anthropic":
            # Claude 3.5 Sonnet: $3/$15 per MTok
            input_cost = (input_tokens / 1_000_000) * 3.0
            output_cost = (output_tokens / 1_000_000) * 15.0
        elif self.provider == "openai":
            # GPT-4o Mini: $0.15/$0.60 per MTok
            input_cost = (input_tokens / 1_000_000) * 0.15
            output_cost = (output_tokens / 1_000_000) * 0.60
        elif self.provider == "deepseek":
            # DeepSeek: $0.28/$0.42 per MTok (cache miss pricing)
            input_cost = (input_tokens / 1_000_000) * 0.28
            output_cost = (output_tokens / 1_000_000) * 0.42
        else:
            return 0.0
        
        return input_cost + output_cost

    def _log_prompt(
        self, track_title: str, artist_name: str, pitch_data: dict[str, Any], cost: float
    ) -> None:
        """Log prompt and response to api_prompts.log."""
        try:
            log_entry = {
                "timestamp": logger.handlers[0].formatter.formatTime(logging.LogRecord("", 0, "", 0, "", (), None))
                if logger.handlers
                else "",
                "service": "pitch_generator",
                "track": f"{artist_name} - {track_title}",
                "model": self.model,
                "cost": cost,
                "elevator_pitch": pitch_data.get("elevator_pitch", ""),
                "tokens": pitch_data.get("tokens", {}),
            }

            # Write to logs/api_prompts.log
            log_file = "logs/api_prompts.log"
            os.makedirs(os.path.dirname(log_file), exist_ok=True)

            with open(log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")

        except Exception as e:
            logger.warning(f"Failed to log prompt: {e}")


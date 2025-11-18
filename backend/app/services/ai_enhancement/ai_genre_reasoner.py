"""AI-powered genre reasoning with narrative explanations."""

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class AIGenreReasoner:
    """AI-powered genre reasoning with commercial context."""

    MAX_COST_PER_REQUEST = 0.005  # Cost governor

    def __init__(self) -> None:
        """Initialize genre reasoner with available API."""
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
                logger.info("✅ Genre reasoner using DeepSeek")
            except Exception as e:
                logger.warning(f"Failed to init DeepSeek: {e}")

        # Fallback to Anthropic
        if not self.client and os.getenv("ANTHROPIC_API_KEY"):
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
                self.model = "claude-3-haiku-20240307"
                self.provider = "anthropic"
                logger.info("✅ Genre reasoner using Anthropic")
            except Exception as e:
                logger.warning(f"Failed to init Anthropic: {e}")

        # Fallback to OpenAI
        if not self.client and os.getenv("OPENAI_API_KEY"):
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                self.model = "gpt-4o-mini"
                self.provider = "openai"
                logger.info("✅ Genre reasoner using OpenAI")
            except Exception as e:
                logger.warning(f"Failed to init OpenAI: {e}")

    def explain_genre(
        self,
        track_title: str,
        artist_name: str,
        sonic_genome: dict[str, Any],
        genre_predictions: dict[str, Any],
        lyrical_themes: list[str] = None
    ) -> dict[str, Any] | None:
        """
        Generate AI explanation of genre classification.
        
        Args:
            track_title: Track title
            artist_name: Artist name
            sonic_genome: Sonic analysis data
            genre_predictions: Existing genre predictions
            lyrical_themes: Extracted themes
        
        Returns:
            Dictionary with genre reasoning and context
        """
        if not self.client:
            logger.warning("No AI provider available - skipping genre reasoning")
            return None

        try:
            # Extract key sonic features
            tempo = sonic_genome.get("tempo", 120)
            energy = sonic_genome.get("energy", 0.5)
            valence = sonic_genome.get("valence", 0.5)
            danceability = sonic_genome.get("danceability", 0.5)
            acousticness = sonic_genome.get("acousticness", 0.5)
            
            # Get top genres
            top_genres = genre_predictions.get("top_genres", [])
            
            # Build prompt
            prompt = self._build_prompt(
                track_title, artist_name, tempo, energy, valence, 
                danceability, acousticness, top_genres, lyrical_themes
            )
            
            # Call AI
            if self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=800,
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}],
                )
                response_text = response.content[0].text
                cost = (response.usage.input_tokens / 1_000_000) * 0.25 + \
                       (response.usage.output_tokens / 1_000_000) * 1.25
            else:  # OpenAI or DeepSeek
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=800,
                )
                response_text = response.choices[0].message.content
                if self.provider == "deepseek":
                    cost = (response.usage.prompt_tokens / 1_000_000) * 0.14 + \
                           (response.usage.completion_tokens / 1_000_000) * 0.28
                else:
                    cost = (response.usage.prompt_tokens / 1_000_000) * 0.15 + \
                           (response.usage.completion_tokens / 1_000_000) * 0.60
            
            # Parse response
            result = self._parse_response(response_text)
            result["cost"] = round(cost, 4)
            result["provider"] = self.provider
            
            logger.info(f"AI genre reasoning complete: ${cost:.4f}")
            return result
            
        except Exception as e:
            logger.error(f"AI genre reasoning failed: {e}")
            return None

    def _build_prompt(
        self, 
        track_title: str, 
        artist_name: str,
        tempo: float,
        energy: float,
        valence: float,
        danceability: float,
        acousticness: float,
        top_genres: list[dict],
        lyrical_themes: list[str]
    ) -> str:
        """Build prompt for genre reasoning."""
        
        genres_str = ", ".join([f"{g['genre']} ({g['confidence']:.0%})" for g in top_genres[:3]]) if top_genres else "Unknown"
        themes_str = ", ".join(lyrical_themes[:5]) if lyrical_themes else "Unknown"
        
        return f"""You are a music genre expert and A&R consultant. Explain WHY this track fits its predicted genres.

**Track:** "{track_title}" by {artist_name}

**Sonic Features:**
- Tempo: {tempo:.0f} BPM
- Energy: {energy:.2f} (0=calm, 1=intense)
- Valence: {valence:.2f} (0=sad, 1=happy)
- Danceability: {danceability:.2f}
- Acousticness: {acousticness:.2f}

**Predicted Genres:** {genres_str}
**Lyrical Themes:** {themes_str}

**Task:** Provide a narrative explanation of the genre(s) with commercial context.

Return JSON with this structure:
{{
  "genre_explanation": "2-3 sentence explanation of WHY this track fits its genre(s). Mention specific sonic characteristics.",
  "subgenre_nuances": "Explain subgenre details (e.g., 'synthwave nostalgia', 'trap-influenced production')",
  "production_style": "Describe production choices that define the genre",
  "comparable_artists": ["Artist 1", "Artist 2", "Artist 3"],
  "target_audience": "Who listens to this genre/style",
  "sync_opportunities": ["Film/TV context 1", "Film/TV context 2"],
  "playlist_fit": ["Playlist name 1", "Playlist name 2", "Playlist name 3"]
}}

IMPORTANT: Be specific. Mention actual sonic features. Return ONLY valid JSON."""

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
            logger.error(f"Failed to parse genre reasoning: {e}")
            return {"error": "Failed to parse response"}


def explain_genre_with_ai(
    track_title: str,
    artist_name: str,
    sonic_genome: dict[str, Any],
    genre_predictions: dict[str, Any],
    lyrical_themes: list[str] = None
) -> dict[str, Any] | None:
    """Convenience function to explain genre with AI."""
    try:
        reasoner = AIGenreReasoner()
        return reasoner.explain_genre(
            track_title, artist_name, sonic_genome, 
            genre_predictions, lyrical_themes
        )
    except Exception as e:
        logger.error(f"AI genre reasoning failed: {e}")
        return None


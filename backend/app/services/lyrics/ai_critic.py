"""AI-powered lyric critique using Claude API."""

import json
import logging
import os
import re
from typing import Any

from anthropic import Anthropic

logger = logging.getLogger(__name__)


class AILyricCritic:
    """AI-powered lyric critique and rewrite suggestions using Claude."""

    MAX_COST_PER_REQUEST = 0.10  # Cost governor: max $0.10 per critique

    def __init__(self):
        """Initialize AI critic with Claude API."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"  # Try latest, fallback handled in code

    def critique(self, lyrics: str, lyrical_genome: dict[str, Any]) -> dict[str, Any]:
        """
        Generate AI critique and rewrite suggestions for lyrics.

        Args:
            lyrics: Full lyrics text
            lyrical_genome: Existing lyrical analysis from VADER

        Returns:
            Dictionary containing critique, suggestions, and cost
        """
        if not lyrics or not lyrics.strip():
            return {
                "error": "No lyrics provided",
                "overall_critique": "Cannot critique empty lyrics.",
                "strengths": [],
                "weaknesses": [],
                "line_by_line_feedback": [],
                "alternative_lines": {},
                "rhyme_scheme_improvements": [],
                "cost": 0.0,
            }

        try:
            # Build prompt with context
            prompt = self._build_prompt(lyrics, lyrical_genome)

            # Try multiple model names for compatibility
            models_to_try = [
                "claude-3-5-sonnet-20241022",
                "claude-3-5-sonnet-20240620", 
                "claude-3-5-sonnet",
                "claude-3-opus-20240229",
                "claude-3-haiku-20240307"
            ]
            
            response = None
            last_error = None
            for model_name in models_to_try:
                try:
                    response = self.client.messages.create(
                        model=model_name,
                        max_tokens=2000,
                        temperature=0.7,
                        messages=[{"role": "user", "content": prompt}],
                    )
                    self.model = model_name  # Update to working model
                    break
                except Exception as e:
                    last_error = e
                    continue
            
            if not response:
                raise last_error or Exception("All model names failed")

            # Calculate cost
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost = self._calculate_cost(input_tokens, output_tokens)

            # Check cost governor
            if cost > self.MAX_COST_PER_REQUEST:
                logger.warning(
                    f"Critique cost ${cost:.4f} exceeds max ${self.MAX_COST_PER_REQUEST}"
                )

            # Parse response
            critique_data = self._parse_response(response.content[0].text)
            critique_data["cost"] = round(cost, 4)
            critique_data["tokens"] = {
                "input": input_tokens,
                "output": output_tokens,
                "total": input_tokens + output_tokens,
            }

            # Log to prompts log
            self._log_prompt(lyrics, lyrical_genome, critique_data, cost)

            return critique_data

        except Exception as e:
            logger.error(f"AI critique failed: {e}")
            return {
                "error": str(e),
                "overall_critique": "AI critique temporarily unavailable.",
                "strengths": [],
                "weaknesses": [],
                "line_by_line_feedback": [],
                "alternative_lines": {},
                "rhyme_scheme_improvements": [],
                "cost": 0.0,
            }

    def _build_prompt(self, lyrics: str, lyrical_genome: dict[str, Any]) -> str:
        """Build critique prompt with context from existing analysis."""
        # Extract key metrics - handle both dict and list formats
        songwriting_quality = lyrical_genome.get("songwriting_quality", {})
        if isinstance(songwriting_quality, dict):
            total_score = songwriting_quality.get("total_score", "N/A")
            grade = songwriting_quality.get("grade", "N/A")
        else:
            total_score = "N/A"
            grade = "N/A"
        
        complexity = lyrical_genome.get("complexity", {})
        if isinstance(complexity, dict):
            vocab_richness = complexity.get("vocabulary_richness", "N/A")
            rhyme_density = complexity.get("rhyme_density", "N/A")
        else:
            vocab_richness = "N/A"
            rhyme_density = "N/A"
        
        themes = lyrical_genome.get("themes", {})
        if isinstance(themes, dict):
            top_themes = themes.get("top_themes", [])
        elif isinstance(themes, list):
            top_themes = themes[:5]  # Take first 5 if it's a list
        else:
            top_themes = []
        
        # Get overall sentiment - check both dict and direct value
        overall_sentiment = lyrical_genome.get("overall_sentiment", "N/A")
        if isinstance(overall_sentiment, dict):
            overall_sentiment = overall_sentiment.get("overall_sentiment", "N/A")
        else:
            overall_sentiment = str(overall_sentiment) if overall_sentiment else "N/A"

        prompt = f"""You are a professional songwriting coach with expertise in lyrical analysis. Analyze these lyrics and provide constructive, actionable feedback.

LYRICS:
{lyrics}

CURRENT ANALYSIS:
- Songwriting Quality: {total_score}/100 (Grade: {grade})
- Vocabulary Richness: {vocab_richness}
- Rhyme Density: {rhyme_density}
- Themes: {', '.join(top_themes) if top_themes else 'None detected'}
- Overall Sentiment: {overall_sentiment}

INSTRUCTIONS:
Provide a detailed critique in the following JSON format:

{{
  "overall_critique": "2-3 sentence summary of the lyrics' strengths and areas for improvement",
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "weaknesses": ["weakness 1", "weakness 2", "weakness 3"],
  "line_by_line_feedback": [
    {{"line_number": 1, "original_line": "...", "feedback": "...", "suggestion": "..."}}
  ],
  "alternative_lines": {{
    "line_3": ["alternative 1", "alternative 2", "alternative 3"]
  }},
  "rhyme_scheme_improvements": ["suggestion 1", "suggestion 2"]
}}

GUIDELINES:
1. Be constructive and specific
2. Focus on craft: imagery, metaphor, rhythm, rhyme, narrative arc
3. Suggest concrete improvements, not just criticisms
4. Consider the genre and emotional tone
5. Provide 3 alternative versions for the weakest lines
6. Keep feedback actionable and encouraging

Return ONLY valid JSON, no additional text."""

        return prompt

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate cost based on Claude 3.5 Sonnet pricing.

        Pricing (as of Nov 2024):
        - Input: $3.00 per million tokens
        - Output: $15.00 per million tokens
        """
        input_cost = (input_tokens / 1_000_000) * 3.00
        output_cost = (output_tokens / 1_000_000) * 15.00
        return input_cost + output_cost

    def _parse_response(self, response_text: str) -> dict[str, Any]:
        """Parse Claude's JSON response."""
        try:
            # Extract JSON from response (in case there's extra text)
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            # Try parsing entire response
            return json.loads(response_text)
        
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            # Return structured fallback
            return {
                "overall_critique": response_text[:500],  # First 500 chars
                "strengths": [],
                "weaknesses": [],
                "line_by_line_feedback": [],
                "alternative_lines": {},
                "rhyme_scheme_improvements": [],
            }

    def _log_prompt(
        self,
        lyrics: str,
        lyrical_genome: dict[str, Any],
        critique: dict[str, Any],
        cost: float,
    ) -> None:
        """Log prompt and response to logs/ai_prompts.log."""
        try:
            log_dir = "logs"
            os.makedirs(log_dir, exist_ok=True)
            
            log_file = os.path.join(log_dir, "ai_prompts.log")
            
            with open(log_file, "a", encoding="utf-8") as f:
                f.write("\n" + "=" * 80 + "\n")
                f.write(f"TIMESTAMP: {self._get_timestamp()}\n")
                f.write(f"MODEL: {self.model}\n")
                f.write(f"COST: ${cost:.4f}\n")
                f.write(f"TOKENS: {critique.get('tokens', {})}\n")
                f.write("\nLYRICS (first 200 chars):\n")
                f.write(lyrics[:200] + "...\n")
                f.write("\nCRITIQUE SUMMARY:\n")
                f.write(critique.get("overall_critique", "N/A")[:200] + "\n")
                f.write("=" * 80 + "\n")
        
        except Exception as e:
            logger.warning(f"Failed to log prompt: {e}")

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat()


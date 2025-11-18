"""Theme extraction using zero-shot classification.

Identifies lyrical themes without training data using HuggingFace
zero-shot classification models.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Try to import transformers
TRANSFORMERS_AVAILABLE = False
try:
    from transformers import pipeline

    TRANSFORMERS_AVAILABLE = True
    logger.info("✅ Transformers available for theme extraction")
except ImportError:
    logger.warning("⚠️ Transformers not available - theme extraction disabled")


class ThemeExtractor:
    """
    Extract themes from lyrics using zero-shot classification.

    Uses facebook/bart-large-mnli for classification without training data.
    """

    # Comprehensive theme taxonomy
    THEME_LABELS = [
        "love",
        "heartbreak",
        "romance",
        "breakup",
        "longing",
        "empowerment",
        "confidence",
        "self-love",
        "independence",
        "resilience",
        "party",
        "celebration",
        "fun",
        "nightlife",
        "dancing",
        "introspection",
        "reflection",
        "melancholy",
        "sadness",
        "depression",
        "loneliness",
        "nostalgia",
        "hope",
        "optimism",
        "dreams",
        "ambition",
        "success",
        "struggle",
        "hardship",
        "poverty",
        "survival",
        "social_commentary",
        "politics",
        "injustice",
        "protest",
        "rebellion",
        "spirituality",
        "faith",
        "religion",
        "existentialism",
        "nature",
        "freedom",
        "travel",
        "adventure",
        "friendship",
        "family",
        "loss",
        "grief",
        "anger",
        "rage",
        "betrayal",
        "jealousy",
        "desire",
        "lust",
        "sexuality",
    ]

    def __init__(self, model_name: str = "facebook/bart-large-mnli") -> None:
        """
        Initialize theme extractor.

        Args:
            model_name: HuggingFace model for zero-shot classification
        """
        self.model_name = model_name
        self.classifier = None

        if TRANSFORMERS_AVAILABLE:
            try:
                logger.info(f"Loading zero-shot model: {model_name}")
                self.classifier = pipeline(
                    "zero-shot-classification", model=model_name, device=-1  # CPU
                )
                logger.info("✅ Theme extraction model loaded")
            except Exception as e:
                logger.error(f"Failed to load theme extraction model: {e}")
                self.classifier = None

    def extract_themes(
        self, lyrics: str, top_n: int = 5, threshold: float = 0.3
    ) -> dict[str, Any]:
        """
        Extract themes from lyrics.

        Args:
            lyrics: Lyrics text
            top_n: Number of top themes to return
            threshold: Minimum confidence threshold (0-1)

        Returns:
            Dictionary with theme scores and explanations
        """
        if not TRANSFORMERS_AVAILABLE or self.classifier is None:
            return {
                "available": False,
                "error": "Theme extraction not available",
                "themes": {},
            }

        if not lyrics or not lyrics.strip():
            return {
                "available": True,
                "themes": {},
                "error": "Empty lyrics",
            }

        try:
            # Run zero-shot classification
            result = self.classifier(
                lyrics,
                candidate_labels=self.THEME_LABELS,
                multi_label=True,  # Multiple themes can apply
            )

            # Extract themes above threshold
            themes = {}
            for label, score in zip(result["labels"], result["scores"]):
                if score >= threshold:
                    themes[label] = round(score, 3)

            # Sort by score and take top N
            sorted_themes = dict(
                sorted(themes.items(), key=lambda x: x[1], reverse=True)[:top_n]
            )

            # Generate theme summary
            summary = self._generate_theme_summary(sorted_themes)

            return {
                "available": True,
                "model": self.model_name,
                "themes": sorted_themes,
                "top_theme": list(sorted_themes.keys())[0]
                if sorted_themes
                else None,
                "theme_count": len(sorted_themes),
                "summary": summary,
            }

        except Exception as e:
            logger.error(f"Theme extraction failed: {e}")
            return {
                "available": True,
                "error": str(e),
                "themes": {},
            }

    def extract_themes_by_section(
        self, lyrics: str, top_n: int = 3
    ) -> dict[str, Any]:
        """
        Extract themes for different sections of lyrics.

        Analyzes verse, chorus, bridge separately if identifiable.

        Args:
            lyrics: Full lyrics
            top_n: Themes per section

        Returns:
            Theme breakdown by section
        """
        if not TRANSFORMERS_AVAILABLE or self.classifier is None:
            return {"available": False}

        # Simple section detection
        sections = self._split_into_sections(lyrics)

        section_themes = {}
        for section_name, section_text in sections.items():
            if section_text.strip():
                themes = self.extract_themes(section_text, top_n=top_n, threshold=0.25)
                section_themes[section_name] = themes.get("themes", {})

        return {
            "available": True,
            "section_themes": section_themes,
            "sections_analyzed": len(section_themes),
        }

    def _split_into_sections(self, lyrics: str) -> dict[str, str]:
        """
        Split lyrics into sections (verse, chorus, bridge).

        Simple heuristic-based approach.

        Args:
            lyrics: Full lyrics

        Returns:
            Dictionary of section_name: section_text
        """
        sections = {"full": lyrics}

        lines = lyrics.split("\n")
        current_section = "verse"
        section_texts = {"verse": [], "chorus": [], "bridge": []}

        for line in lines:
            line_lower = line.lower().strip()

            # Detect section markers
            if any(marker in line_lower for marker in ["[chorus]", "(chorus)", "chorus:"]):
                current_section = "chorus"
                continue
            elif any(marker in line_lower for marker in ["[verse]", "(verse)", "verse"]):
                current_section = "verse"
                continue
            elif any(marker in line_lower for marker in ["[bridge]", "(bridge)", "bridge:"]):
                current_section = "bridge"
                continue

            # Add line to current section
            if line.strip():
                section_texts[current_section].append(line)

        # Join sections
        for section, lines in section_texts.items():
            if lines:
                sections[section] = "\n".join(lines)

        return sections

    def _generate_theme_summary(self, themes: dict[str, float]) -> str:
        """
        Generate human-readable theme summary.

        Args:
            themes: Dictionary of theme: score

        Returns:
            Summary string
        """
        if not themes:
            return "No clear themes detected"

        top_themes = list(themes.keys())[:3]

        if len(top_themes) == 1:
            return f"Primary theme: {top_themes[0]}"
        elif len(top_themes) == 2:
            return f"Themes: {top_themes[0]} and {top_themes[1]}"
        else:
            return f"Themes: {', '.join(top_themes[:-1])}, and {top_themes[-1]}"


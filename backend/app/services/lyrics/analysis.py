"""Lyrics analysis using VADER sentiment and NLP."""

import logging
import re
from typing import Any

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from .ai_lyrics_critic import critique_lyrics_with_ai
from .ai_section_detector import analyze_sections_with_ai

logger = logging.getLogger(__name__)


class LyricsAnalyzer:
    """Analyze lyrics for sentiment, themes, and structure."""

    def __init__(self):
        """Initialize lyrics analyzer."""
        self.vader = SentimentIntensityAnalyzer()

    def analyze_lyrics(self, lyrics: str, track_title: str = "", artist_name: str = "") -> dict[str, Any]:
        """
        Perform comprehensive lyrical analysis.

        Args:
            lyrics: Full lyrics text
            track_title: Track title for AI context (optional)
            artist_name: Artist name for AI context (optional)

        Returns:
            Dictionary containing lyrical genome
        """
        # Clean and structure lyrics
        lines = self._clean_lyrics(lyrics)
        sections = self._detect_sections(lyrics, track_title, artist_name)

        # Sentiment analysis
        emotional_arc = self._compute_emotional_arc(lines)
        overall_sentiment = self._compute_overall_sentiment(lyrics)

        # Structural analysis
        structure = self._analyze_structure(sections)

        # Thematic analysis (keyword-based for now)
        themes = self._extract_themes(lyrics)

        # Complexity metrics
        complexity = self._compute_complexity(lyrics, lines)

        # Hook/repetition analysis
        repetition = self._analyze_repetition(lines)

        # Songwriting quality score
        songwriting_quality = self._analyze_songwriting_quality(
            sections, emotional_arc, complexity, repetition, structure
        )

        # AI-powered lyrics critique (new ungated feature!)
        logger.info("Attempting AI-powered lyrics critique...")
        ai_critique = critique_lyrics_with_ai(
            lyrics,
            track_title=track_title,
            artist_name=artist_name,
            sections=sections,
            themes=themes,
            sentiment=overall_sentiment
        )
        if ai_critique:
            logger.info(f"✅ AI lyrics critique successful: {ai_critique.get('overall_rating', 'N/A')}/10")
        else:
            logger.info("AI critique unavailable - skipping")

        return {
            "overall_sentiment": overall_sentiment,
            "emotional_arc": emotional_arc,
            "structure": structure,
            "themes": themes,
            "complexity": complexity,
            "repetition": repetition,
            "songwriting_quality": songwriting_quality,
            "ai_critique": ai_critique,  # NEW: AI-powered critique
            "line_count": len(lines),
            "word_count": len(lyrics.split()),
            "sections": sections,
        }

    def _clean_lyrics(self, lyrics: str) -> list[str]:
        """Clean and split lyrics into lines."""
        # Remove extra whitespace and split by lines
        lines = [line.strip() for line in lyrics.split("\n") if line.strip()]
        # Remove section markers from lines
        return [line for line in lines if not re.match(r"^\[.*\]$", line)]

    def _detect_sections(self, lyrics: str, track_title: str = "", artist_name: str = "") -> list[dict[str, str]]:
        """
        Detect song sections (verse, chorus, bridge, etc.).
        
        First tries AI-powered detection for accurate results.
        Falls back to explicit markers like [Verse 1], [Chorus].
        Falls back to heuristic detection based on blank lines if no markers found.

        Args:
            lyrics: Full lyrics text
            track_title: Track title for AI context (optional)
            artist_name: Artist name for AI context (optional)

        Returns:
            List of sections with type and content
        """
        # Try AI-powered detection first (most accurate)
        logger.info("Attempting AI-powered section detection...")
        ai_result = analyze_sections_with_ai(lyrics, track_title, artist_name)
        if ai_result and "sections" in ai_result and ai_result["sections"]:
            logger.info(f"✅ AI section detection successful: {len(ai_result['sections'])} sections")
            return ai_result["sections"]
        
        logger.info("AI detection unavailable, falling back to heuristic detection")
        
        # Fallback to explicit marker detection
        sections = []
        current_section = None
        current_lines = []

        for line in lyrics.split("\n"):
            line = line.strip()

            # Check if line is a section marker
            section_match = re.match(r"^\[(.*?)\]$", line)
            if section_match:
                # Save previous section
                if current_section:
                    sections.append(
                        {
                            "type": current_section,
                            "content": "\n".join(current_lines),
                            "line_count": len(current_lines),
                        }
                    )

                # Start new section
                current_section = section_match.group(1).lower()
                current_lines = []
            elif line:
                current_lines.append(line)

        # Add final section
        if current_section and current_lines:
            sections.append(
                {
                    "type": current_section,
                    "content": "\n".join(current_lines),
                    "line_count": len(current_lines),
                }
            )

        # If no explicit sections found, use heuristic detection
        if not sections:
            sections = self._detect_sections_heuristic(lyrics)

        return sections

    def _detect_sections_heuristic(self, lyrics: str) -> list[dict[str, str]]:
        """
        Heuristically detect sections based on blank lines and repetition patterns.
        Assigns section types based on content analysis and position.

        Args:
            lyrics: Full lyrics text

        Returns:
            List of detected sections
        """
        # Split by blank lines (multiple newlines)
        raw_sections = re.split(r"\n\s*\n", lyrics)
        
        if not raw_sections or len(raw_sections) < 2:
            # If only one section, treat entire lyrics as a single section
            lines = [l.strip() for l in lyrics.split("\n") if l.strip()]
            if lines:
                return [{
                    "type": "lyrics",
                    "content": "\n".join(lines),
                    "line_count": len(lines),
                }]
            return []

        sections = []
        repetition_map = {}  # Track which content repeats
        
        # First pass: identify repeated sections (likely choruses)
        for i, section_text in enumerate(raw_sections):
            section_lines = [l.strip() for l in section_text.split("\n") if l.strip()]
            if not section_lines:
                continue
            
            # Normalize for comparison (remove minor variations)
            normalized = " ".join(section_lines).lower()
            if normalized not in repetition_map:
                repetition_map[normalized] = []
            repetition_map[normalized].append(i)
        
        # Second pass: assign section types
        for i, section_text in enumerate(raw_sections):
            section_lines = [l.strip() for l in section_text.split("\n") if l.strip()]
            if not section_lines:
                continue
            
            normalized = " ".join(section_lines).lower()
            repeat_count = len(repetition_map[normalized])
            
            # Assign type based on heuristics
            if repeat_count > 1:
                # Repeated sections are likely choruses
                section_type = "chorus"
            elif i == 0:
                # First section is usually verse or intro
                section_type = "verse 1" if len(section_lines) > 2 else "intro"
            elif i == len(raw_sections) - 1:
                # Last section could be outro or final verse
                section_type = "outro" if len(section_lines) <= 2 else "verse"
            else:
                # Middle sections alternate between verse and bridge
                verse_count = sum(1 for s in sections if "verse" in s["type"])
                if verse_count >= 2:
                    section_type = "bridge"
                else:
                    section_type = f"verse {verse_count + 2}"
            
            sections.append({
                "type": section_type,
                "content": "\n".join(section_lines),
                "line_count": len(section_lines),
            })
        
        return sections

    def _compute_emotional_arc(self, lines: list[str]) -> list[dict[str, float]]:
        """
        Compute sentiment arc across the song.

        Args:
            lines: List of lyric lines

        Returns:
            List of sentiment scores per line
        """
        arc = []

        for i, line in enumerate(lines):
            if not line:
                continue

            scores = self.vader.polarity_scores(line)
            arc.append(
                {
                    "line_index": i,
                    "positive": scores["pos"],
                    "negative": scores["neg"],
                    "neutral": scores["neu"],
                    "compound": scores["compound"],
                }
            )

        return arc

    def _compute_overall_sentiment(self, lyrics: str) -> dict[str, float]:
        """Compute overall sentiment for entire lyrics."""
        scores = self.vader.polarity_scores(lyrics)

        # Classify overall mood
        compound = scores["compound"]
        if compound >= 0.05:
            mood = "positive"
        elif compound <= -0.05:
            mood = "negative"
        else:
            mood = "neutral"

        return {
            "positive": scores["pos"],
            "negative": scores["neg"],
            "neutral": scores["neu"],
            "compound": scores["compound"],
            "mood": mood,
        }

    def _analyze_structure(self, sections: list[dict[str, str]]) -> dict[str, Any]:
        """Analyze song structure."""
        section_types = [s["type"] for s in sections]

        # Count section types
        section_counts = {}
        for section_type in section_types:
            section_counts[section_type] = section_counts.get(section_type, 0) + 1

        # Detect structure pattern
        pattern = " -> ".join(section_types)

        return {
            "pattern": pattern,
            "section_counts": section_counts,
            "total_sections": len(sections),
            "has_bridge": any("bridge" in s for s in section_types),
            "has_pre_chorus": any("pre" in s and "chorus" in s for s in section_types),
        }

    def _extract_themes(self, lyrics: str) -> list[str]:
        """
        Extract themes using keyword matching.

        This is a simple implementation. In production, use:
        - Local LLM (Ollama) for deeper thematic analysis
        - Or API calls to Claude/GPT for thematic extraction
        """
        lyrics_lower = lyrics.lower()

        # Theme keyword dictionary
        theme_keywords = {
            "love": ["love", "heart", "kiss", "romance", "together", "forever"],
            "heartbreak": ["pain", "tears", "goodbye", "alone", "broken", "lost"],
            "party": ["party", "dance", "night", "club", "drink", "celebrate"],
            "empowerment": ["strong", "power", "rise", "fight", "stand", "free"],
            "nostalgia": ["remember", "past", "yesterday", "memories", "used to"],
            "social_commentary": ["world", "people", "society", "change", "justice"],
            "introspection": ["myself", "who am i", "wonder", "think", "feel", "soul"],
            "rebellion": ["rebel", "break", "rules", "against", "fight", "revolution"],
            "spirituality": ["god", "faith", "pray", "heaven", "soul", "believe"],
            "nature": ["sky", "sun", "moon", "stars", "ocean", "mountain", "rain"],
        }

        detected_themes = []
        for theme, keywords in theme_keywords.items():
            if any(keyword in lyrics_lower for keyword in keywords):
                detected_themes.append(theme)

        return detected_themes[:5]  # Return top 5 themes

    def _compute_complexity(self, lyrics: str, lines: list[str]) -> dict[str, Any]:
        """Compute lyrical complexity metrics."""
        words = lyrics.lower().split()
        unique_words = set(words)

        # Vocabulary richness
        vocabulary_richness = len(unique_words) / len(words) if words else 0

        # Average line length
        avg_line_length = (
            sum(len(line.split()) for line in lines) / len(lines) if lines else 0
        )

        # Rhyme detection (simplified - check last words)
        rhyme_score = self._estimate_rhyme_density(lines)

        return {
            "vocabulary_richness": float(vocabulary_richness),
            "unique_word_count": len(unique_words),
            "total_word_count": len(words),
            "avg_line_length": float(avg_line_length),
            "rhyme_density": float(rhyme_score),
        }

    def _estimate_rhyme_density(self, lines: list[str]) -> float:
        """Estimate rhyme density by checking last words."""
        if len(lines) < 2:
            return 0.0

        last_words = []
        for line in lines:
            words = line.split()
            if words:
                last_words.append(words[-1].lower().strip(".,!?;:"))

        # Count pairs of similar-ending words (simple rhyme detection)
        rhyme_count = 0
        for i in range(len(last_words) - 1):
            word1 = last_words[i]
            word2 = last_words[i + 1]

            # Check if last 2-3 characters match (simple rhyme)
            if (
                len(word1) >= 2
                and len(word2) >= 2
                and (word1[-2:] == word2[-2:] or word1[-3:] == word2[-3:])
            ):
                rhyme_count += 1

        return rhyme_count / (len(last_words) - 1) if len(last_words) > 1 else 0

    def _analyze_repetition(self, lines: list[str]) -> dict[str, Any]:
        """Analyze repetition and hook potential."""
        # Find most repeated lines (potential hooks)
        line_counts = {}
        for line in lines:
            line_lower = line.lower().strip()
            if len(line_lower) > 10:  # Ignore very short lines
                line_counts[line_lower] = line_counts.get(line_lower, 0) + 1

        # Find most repeated line
        if line_counts:
            most_repeated = max(line_counts.items(), key=lambda x: x[1])
            most_repeated_line = most_repeated[0]
            repetition_count = most_repeated[1]
        else:
            most_repeated_line = None
            repetition_count = 0

        # Compute repetition score
        total_lines = len(lines)
        repetition_score = (
            (repetition_count / total_lines * 100) if total_lines > 0 else 0
        )

        return {
            "most_repeated_line": most_repeated_line,
            "repetition_count": repetition_count,
            "repetition_score": float(repetition_score),
            "has_strong_hook": repetition_count >= 3,
        }

    def _analyze_songwriting_quality(
        self,
        sections: list[dict[str, str]],
        emotional_arc: list[dict[str, float]],
        complexity: dict[str, Any],
        repetition: dict[str, Any],
        structure: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Analyze songwriting quality (0-100 score).
        
        Evaluates:
        - Song structure (verse/chorus/bridge arrangement)
        - Hook effectiveness (does the hook provide relief?)
        - Narrative arc (emotional journey)
        - Lyrical craft (rhyme, vocabulary, imagery)
        - Commercial viability
        """
        scores = {}
        
        # 1. Structure Quality (0-25 points)
        structure_score = self._score_structure_quality(sections, structure)
        scores["structure_quality"] = structure_score
        
        # 2. Hook Effectiveness (0-25 points)
        hook_score = self._score_hook_effectiveness(sections, emotional_arc, repetition)
        scores["hook_effectiveness"] = hook_score
        
        # 3. Narrative Arc (0-25 points)
        narrative_score = self._score_narrative_arc(emotional_arc, sections)
        scores["narrative_arc"] = narrative_score
        
        # 4. Lyrical Craft (0-25 points)
        craft_score = self._score_lyrical_craft(complexity, sections)
        scores["lyrical_craft"] = craft_score
        
        # Overall songwriting quality
        overall = sum(scores.values())
        
        # Generate insights
        insights = self._generate_songwriting_insights(scores, structure, sections)
        
        return {
            "overall_score": round(overall, 1),
            "grade": self._get_songwriting_grade(overall),
            "components": {
                "structure_quality": {"score": round(structure_score, 1), "max": 25},
                "hook_effectiveness": {"score": round(hook_score, 1), "max": 25},
                "narrative_arc": {"score": round(narrative_score, 1), "max": 25},
                "lyrical_craft": {"score": round(craft_score, 1), "max": 25},
            },
            "insights": insights,
        }
    
    def _score_structure_quality(
        self, sections: list[dict[str, str]], structure: dict[str, Any]
    ) -> float:
        """Score song structure (0-25)."""
        score = 0.0
        
        # Has clear verse/chorus structure (0-10 points)
        section_types = [s["type"] for s in sections]
        has_verse = any("verse" in s for s in section_types)
        has_chorus = any("chorus" in s for s in section_types)
        
        if has_verse and has_chorus:
            score += 10.0
        elif has_verse or has_chorus:
            score += 6.0
        else:
            score += 3.0  # Unconventional structure
        
        # Has bridge (0-5 points) - adds variety
        if structure.get("has_bridge"):
            score += 5.0
        else:
            score += 2.0
        
        # Has pre-chorus (0-5 points) - builds tension
        if structure.get("has_pre_chorus"):
            score += 5.0
        else:
            score += 3.0
        
        # Section balance (0-5 points)
        section_counts = structure.get("section_counts", {})
        chorus_count = section_counts.get("chorus", 0)
        
        if 2 <= chorus_count <= 4:  # Ideal repetition
            score += 5.0
        elif 1 <= chorus_count <= 5:
            score += 3.0
        else:
            score += 1.0
        
        return min(score, 25.0)
    
    def _score_hook_effectiveness(
        self,
        sections: list[dict[str, str]],
        emotional_arc: list[dict[str, float]],
        repetition: dict[str, Any],
    ) -> float:
        """
        Score hook effectiveness (0-25).
        
        Does the hook provide relief? (Tension → Release)
        """
        score = 0.0
        
        # Strong hook repetition (0-10 points)
        if repetition.get("has_strong_hook"):
            rep_score = min(repetition.get("repetition_score", 0) / 10, 1.0)
            score += rep_score * 10
        else:
            score += 3.0
        
        # Emotional relief analysis (0-10 points)
        # Check if chorus provides emotional lift
        chorus_sections = [s for s in sections if "chorus" in s["type"]]
        
        if chorus_sections and emotional_arc:
            # Find chorus sentiment
            chorus_sentiment = []
            for section in chorus_sections:
                # Approximate: assume chorus is in middle-to-end of song
                mid_point = len(emotional_arc) // 2
                chorus_sentiment.extend(
                    [point["compound"] for point in emotional_arc[mid_point:]]
                )
            
            if chorus_sentiment:
                avg_chorus_sentiment = sum(chorus_sentiment) / len(chorus_sentiment)
                
                # Positive chorus = relief/catharsis
                if avg_chorus_sentiment > 0.2:
                    score += 10.0
                elif avg_chorus_sentiment > 0:
                    score += 7.0
                else:
                    score += 4.0  # Dark/melancholic hook (still valid)
            else:
                score += 5.0
        else:
            score += 5.0  # Neutral if no data
        
        # Memorability (0-5 points)
        # Short, punchy lines are more memorable
        if repetition.get("most_repeated_line"):
            line_length = len(repetition["most_repeated_line"].split())
            if line_length <= 8:  # Short and catchy
                score += 5.0
            elif line_length <= 12:
                score += 3.0
            else:
                score += 1.0
        else:
            score += 2.0
        
        return min(score, 25.0)
    
    def _score_narrative_arc(
        self, emotional_arc: list[dict[str, float]], sections: list[dict[str, str]]
    ) -> float:
        """Score narrative/emotional arc (0-25)."""
        score = 0.0
        
        if not emotional_arc or len(emotional_arc) < 3:
            return 10.0  # Neutral score
        
        # Extract compound sentiment values
        compounds = [point["compound"] for point in emotional_arc]
        
        # 1. Emotional range (0-10 points)
        # Good songs have emotional dynamics
        sentiment_range = max(compounds) - min(compounds)
        
        if sentiment_range > 0.6:  # Wide emotional range
            score += 10.0
        elif sentiment_range > 0.4:
            score += 7.0
        elif sentiment_range > 0.2:
            score += 5.0
        else:
            score += 3.0  # Flat emotional arc
        
        # 2. Emotional journey (0-10 points)
        # Check for clear progression (not just random)
        # Calculate variance in first vs second half
        mid = len(compounds) // 2
        first_half_avg = sum(compounds[:mid]) / mid if mid > 0 else 0
        second_half_avg = sum(compounds[mid:]) / (len(compounds) - mid) if len(compounds) > mid else 0
        
        # Reward clear shift (either direction)
        shift = abs(second_half_avg - first_half_avg)
        if shift > 0.3:
            score += 10.0
        elif shift > 0.15:
            score += 7.0
        else:
            score += 4.0
        
        # 3. Resolution (0-5 points)
        # Does the song end on a clear note?
        final_sentiment = compounds[-1]
        if abs(final_sentiment) > 0.3:  # Clear ending (happy or sad)
            score += 5.0
        else:
            score += 3.0  # Ambiguous ending (also valid)
        
        return min(score, 25.0)
    
    def _score_lyrical_craft(
        self, complexity: dict[str, Any], sections: list[dict[str, str]]
    ) -> float:
        """Score lyrical craft (0-25)."""
        score = 0.0
        
        # 1. Vocabulary richness (0-8 points)
        vocab_richness = complexity.get("vocabulary_richness", 0)
        if vocab_richness > 0.6:
            score += 8.0
        elif vocab_richness > 0.4:
            score += 6.0
        elif vocab_richness > 0.25:
            score += 4.0
        else:
            score += 2.0
        
        # 2. Rhyme density (0-8 points)
        rhyme_density = complexity.get("rhyme_density", 0)
        if 0.05 <= rhyme_density <= 0.20:  # Sweet spot
            score += 8.0
        elif rhyme_density > 0:
            score += 5.0
        else:
            score += 2.0
        
        # 3. Line length variety (0-5 points)
        avg_line_length = complexity.get("avg_line_length", 0)
        if 6 <= avg_line_length <= 12:  # Good range
            score += 5.0
        else:
            score += 3.0
        
        # 4. Imagery/specificity (0-4 points)
        # More unique words = more specific imagery
        if vocab_richness > 0.5:
            score += 4.0
        elif vocab_richness > 0.3:
            score += 3.0
        else:
            score += 2.0
        
        return min(score, 25.0)
    
    def _get_songwriting_grade(self, score: float) -> str:
        """Convert score to letter grade."""
        if score >= 90:
            return "A+"
        elif score >= 85:
            return "A"
        elif score >= 80:
            return "A-"
        elif score >= 75:
            return "B+"
        elif score >= 70:
            return "B"
        elif score >= 65:
            return "B-"
        elif score >= 60:
            return "C+"
        elif score >= 55:
            return "C"
        elif score >= 50:
            return "C-"
        else:
            return "D"
    
    def _generate_songwriting_insights(
        self,
        scores: dict[str, float],
        structure: dict[str, Any],
        sections: list[dict[str, str]],
    ) -> list[str]:
        """Generate actionable songwriting insights."""
        insights = []
        
        # Structure feedback
        if scores["structure_quality"] < 15:
            if not structure.get("has_bridge"):
                insights.append("🎵 Consider adding a bridge for variety and contrast")
            if not structure.get("has_pre_chorus"):
                insights.append("🎵 A pre-chorus could build tension before the hook")
        elif scores["structure_quality"] >= 20:
            insights.append("✅ Strong song structure with clear sections")
        
        # Hook feedback
        if scores["hook_effectiveness"] < 15:
            insights.append("🎣 Strengthen the hook - make it more memorable and repetitive")
        elif scores["hook_effectiveness"] >= 20:
            insights.append("✅ Effective hook that provides emotional payoff")
        
        # Narrative feedback
        if scores["narrative_arc"] < 15:
            insights.append("📖 Develop a clearer emotional journey throughout the song")
        elif scores["narrative_arc"] >= 20:
            insights.append("✅ Compelling narrative arc with emotional dynamics")
        
        # Craft feedback
        if scores["lyrical_craft"] < 15:
            insights.append("✍️ Enhance vocabulary and imagery for more vivid storytelling")
        elif scores["lyrical_craft"] >= 20:
            insights.append("✅ Sophisticated lyrical craft with strong imagery")
        
        return insights[:4]  # Return top 4 insights


# Convenience function
def analyze_lyrics(lyrics: str) -> dict[str, Any]:
    """
    Analyze lyrics and return lyrical genome.

    Args:
        lyrics: Full lyrics text

    Returns:
        Lyrical genome dictionary
    """
    analyzer = LyricsAnalyzer()
    return analyzer.analyze_lyrics(lyrics)

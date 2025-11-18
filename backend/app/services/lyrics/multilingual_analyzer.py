"""Multilingual lyrical analysis with translation and NER.

Supports automatic language detection, translation to English,
and entity extraction using spaCy.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Try to import dependencies
LANGDETECT_AVAILABLE = False
TRANSLATOR_AVAILABLE = False
SPACY_AVAILABLE = False

try:
    from langdetect import detect, LangDetectException

    LANGDETECT_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ langdetect not available - language detection disabled")

try:
    from deep_translator import GoogleTranslator

    TRANSLATOR_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ deep-translator not available - translation disabled")

try:
    import spacy

    SPACY_AVAILABLE = True
    # Try to load English model
    try:
        nlp = spacy.load("en_core_web_sm")
        logger.info("✅ spaCy English model loaded")
    except OSError:
        logger.warning(
            "⚠️ spaCy en_core_web_sm model not found. "
            "Download with: python -m spacy download en_core_web_sm"
        )
        nlp = None
except ImportError:
    logger.warning("⚠️ spaCy not available - NER disabled")
    nlp = None


class MultilingualAnalyzer:
    """
    Analyze lyrics in multiple languages.

    Features:
    - Language detection
    - Translation to English
    - Named Entity Recognition (NER)
    - Linguistic features
    """

    def __init__(self) -> None:
        """Initialize multilingual analyzer."""
        self.has_langdetect = LANGDETECT_AVAILABLE
        self.has_translator = TRANSLATOR_AVAILABLE
        self.has_spacy = SPACY_AVAILABLE and nlp is not None

    def analyze(self, lyrics: str) -> dict[str, Any]:
        """
        Perform multilingual analysis on lyrics.

        Args:
            lyrics: Lyrics text

        Returns:
            Analysis including language, translation, and entities
        """
        if not lyrics or not lyrics.strip():
            return {
                "language": "unknown",
                "translation": None,
                "entities": [],
                "error": "Empty lyrics",
            }

        # Detect language
        language = self._detect_language(lyrics)

        # Translate if not English
        translation = None
        translated_text = lyrics  # Use original if no translation needed

        if language != "en" and language != "unknown":
            translation = self._translate_to_english(lyrics, language)
            if translation:
                translated_text = translation

        # Extract entities (from English text)
        entities = self._extract_entities(translated_text)

        # Linguistic features
        linguistic_features = self._extract_linguistic_features(translated_text)

        return {
            "language": language,
            "language_detected": language != "unknown",
            "translation": translation,
            "was_translated": translation is not None,
            "entities": entities,
            "linguistic_features": linguistic_features,
        }

    def _detect_language(self, text: str) -> str:
        """
        Detect language of text.

        Args:
            text: Input text

        Returns:
            ISO 639-1 language code (e.g., 'en', 'es', 'fr')
        """
        if not self.has_langdetect:
            return "unknown"

        try:
            lang = detect(text)
            logger.info(f"Detected language: {lang}")
            return lang
        except LangDetectException as e:
            logger.warning(f"Language detection failed: {e}")
            return "unknown"

    def _translate_to_english(self, text: str, source_lang: str) -> str | None:
        """
        Translate text to English.

        Args:
            text: Text to translate
            source_lang: Source language code

        Returns:
            Translated text or None if translation fails
        """
        if not self.has_translator:
            return None

        try:
            # GoogleTranslator uses free Google Translate
            translator = GoogleTranslator(source=source_lang, target="en")

            # Split into chunks if text is long (GoogleTranslator has limits)
            max_length = 4500
            if len(text) > max_length:
                chunks = [text[i : i + max_length] for i in range(0, len(text), max_length)]
                translated_chunks = [translator.translate(chunk) for chunk in chunks]
                translated = " ".join(translated_chunks)
            else:
                translated = translator.translate(text)

            logger.info(f"Translated from {source_lang} to en")
            return translated

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return None

    def _extract_entities(self, text: str) -> list[dict[str, str]]:
        """
        Extract named entities using spaCy.

        Args:
            text: Text to analyze (preferably English)

        Returns:
            List of entities with text and label
        """
        if not self.has_spacy:
            return []

        try:
            doc = nlp(text)  # type: ignore
            entities = []

            for ent in doc.ents:
                entities.append(
                    {
                        "text": ent.text,
                        "label": ent.label_,
                        "start": ent.start_char,
                        "end": ent.end_char,
                    }
                )

            logger.info(f"Extracted {len(entities)} entities")
            return entities

        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return []

    def _extract_linguistic_features(self, text: str) -> dict[str, Any]:
        """
        Extract linguistic features using spaCy.

        Args:
            text: Text to analyze

        Returns:
            Dictionary of linguistic features
        """
        if not self.has_spacy:
            return {}

        try:
            doc = nlp(text)  # type: ignore

            # Part-of-speech counts
            pos_counts = {}
            for token in doc:
                pos = token.pos_
                pos_counts[pos] = pos_counts.get(pos, 0) + 1

            # Sentence count
            sentence_count = len(list(doc.sents))

            # Token count
            token_count = len(doc)

            # Average sentence length
            avg_sentence_length = token_count / sentence_count if sentence_count > 0 else 0

            # Lexical diversity (unique words / total words)
            unique_words = len(set([token.text.lower() for token in doc if token.is_alpha]))
            alpha_tokens = len([token for token in doc if token.is_alpha])
            lexical_diversity = unique_words / alpha_tokens if alpha_tokens > 0 else 0

            return {
                "sentence_count": sentence_count,
                "token_count": token_count,
                "avg_sentence_length": round(avg_sentence_length, 2),
                "lexical_diversity": round(lexical_diversity, 3),
                "pos_distribution": pos_counts,
                "unique_words": unique_words,
            }

        except Exception as e:
            logger.error(f"Linguistic feature extraction failed: {e}")
            return {}


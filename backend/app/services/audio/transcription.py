"""Audio transcription using OpenAI Whisper."""

import logging
import os
from difflib import SequenceMatcher
from typing import Any

import whisper

logger = logging.getLogger(__name__)


class AudioTranscriber:
    """Transcribe lyrics from audio using Whisper."""

    def __init__(self, model_size: str = "small"):
        """
        Initialize audio transcriber.
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
                       - tiny: Fastest, least accurate (~1GB RAM)
                       - base: Good balance (~1GB RAM)
                       - small: Better accuracy (~2GB RAM) ← DEFAULT (upgraded for better lyrics)
                       - medium: High accuracy (~5GB RAM)
                       - large: Best accuracy (~10GB RAM)
        """
        self.model_size = model_size
        self._model = None
        logger.info(f"AudioTranscriber initialized with model size: {model_size}")

    @property
    def model(self):
        """Lazy load the Whisper model."""
        if self._model is None:
            logger.info(f"Loading Whisper model: {self.model_size}")
            self._model = whisper.load_model(self.model_size)
            logger.info("Whisper model loaded successfully")
        return self._model

    def transcribe_lyrics(
        self, 
        audio_path: str,
        language: str = "en",
        task: str = "transcribe"
    ) -> dict[str, Any]:
        """
        Transcribe lyrics from audio using Whisper.
        
        Args:
            audio_path: Path to audio file
            language: Language code (e.g., "en", "es", "fr") or None for auto-detect
            task: "transcribe" or "translate" (translate to English)
        
        Returns:
            {
                "text": "full lyrics",
                "segments": [{"start": 0.0, "end": 5.2, "text": "line 1"}],
                "language": "en",
                "confidence": 0.85
            }
        """
        try:
            logger.info(f"Transcribing audio: {audio_path}")
            
            # Transcribe with Whisper
            result = self.model.transcribe(
                audio_path,
                language=language if language != "auto" else None,
                task=task,
                fp16=False,  # CPU compatibility
                verbose=False,
            )
            
            # Calculate average confidence from segments
            if result.get("segments"):
                # Whisper doesn't always provide confidence, estimate from no_speech_prob
                confidences = []
                for seg in result["segments"]:
                    # Lower no_speech_prob = higher confidence
                    no_speech = seg.get("no_speech_prob", 0.5)
                    confidence = 1.0 - no_speech
                    confidences.append(confidence)
                
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0.7
            else:
                avg_confidence = 0.7  # Default moderate confidence
            
            logger.info(
                f"Transcription complete. Language: {result.get('language')}, "
                f"Confidence: {avg_confidence:.2f}"
            )
            
            return {
                "text": result["text"].strip(),
                "segments": result.get("segments", []),
                "language": result.get("language", language),
                "confidence": round(avg_confidence, 2),
                "success": True,
            }
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return {
                "text": "",
                "segments": [],
                "language": language,
                "confidence": 0.0,
                "success": False,
                "error": str(e),
            }

    def compare_lyrics(
        self, 
        provided_lyrics: str, 
        detected_lyrics: str
    ) -> dict[str, Any]:
        """
        Compare user-provided lyrics with detected lyrics.
        
        Returns similarity score and suggestions.
        
        Args:
            provided_lyrics: User-provided lyrics text
            detected_lyrics: Auto-detected lyrics from Whisper
        
        Returns:
            {
                "similarity_score": 0.87,
                "status": "good_match",
                "message": "✓ Lyrics mostly match",
                "detected_lyrics": "...",  # Only if similarity < 0.80
                "differences": [...],  # List of differences
            }
        """
        # Normalize both texts
        provided = self._normalize_text(provided_lyrics)
        detected = self._normalize_text(detected_lyrics)
        
        # Calculate similarity using SequenceMatcher
        similarity = SequenceMatcher(None, provided, detected).ratio()
        
        # Determine status and message
        if similarity > 0.95:
            status = "excellent_match"
            message = "✅ Lyrics match detected audio perfectly"
            include_detected = False
        elif similarity > 0.80:
            status = "good_match"
            message = "✓ Lyrics mostly match (minor differences detected)"
            include_detected = False
        elif similarity > 0.60:
            status = "partial_match"
            message = "⚠️ Some differences detected. Please verify lyrics."
            include_detected = True
        elif similarity > 0.30:
            status = "poor_match"
            message = "❌ Significant mismatch. Detected lyrics may be more accurate."
            include_detected = True
        else:
            status = "no_match"
            message = "❌ Lyrics don't match audio. Consider using detected lyrics."
            include_detected = True
        
        # Find differences (simple word-level diff)
        differences = self._find_differences(provided, detected)
        
        result = {
            "similarity_score": round(similarity, 2),
            "status": status,
            "message": message,
            "has_differences": similarity < 1.0,
        }
        
        # Only include detected lyrics if there's a significant mismatch
        if include_detected:
            result["detected_lyrics"] = detected_lyrics
            result["differences"] = differences[:10]  # Limit to 10 differences
        
        return result

    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        import re
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove section markers like [Verse], [Chorus], etc.
        text = re.sub(r'\[.*?\]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove punctuation (keep apostrophes)
        text = re.sub(r'[^\w\s\']', '', text)
        
        return text.strip()

    def _find_differences(self, text1: str, text2: str) -> list[dict[str, str]]:
        """Find word-level differences between two texts."""
        words1 = text1.split()
        words2 = text2.split()
        
        differences = []
        matcher = SequenceMatcher(None, words1, words2)
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                differences.append({
                    "type": "replace",
                    "provided": ' '.join(words1[i1:i2]),
                    "detected": ' '.join(words2[j1:j2]),
                })
            elif tag == 'delete':
                differences.append({
                    "type": "delete",
                    "provided": ' '.join(words1[i1:i2]),
                    "detected": "",
                })
            elif tag == 'insert':
                differences.append({
                    "type": "insert",
                    "provided": "",
                    "detected": ' '.join(words2[j1:j2]),
                })
        
        return differences


# Singleton instance (lazy-loaded)
_transcriber_instance = None


def get_transcriber(model_size: str | None = None) -> AudioTranscriber:
    """
    Get or create transcriber instance.
    
    Args:
        model_size: Whisper model size. If None, uses WHISPER_MODEL_SIZE env var or "small" default.
    """
    global _transcriber_instance
    
    # Determine model size from env var if not specified
    if model_size is None:
        model_size = os.getenv("WHISPER_MODEL_SIZE", "small")
    
    if _transcriber_instance is None:
        _transcriber_instance = AudioTranscriber(model_size)
    return _transcriber_instance


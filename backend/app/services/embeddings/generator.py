"""Generate embeddings using sentence-transformers."""

import logging

import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generate embeddings for text using sentence-transformers."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding generator.

        Args:
            model_name: Name of the sentence-transformers model
        """
        self.model_name = model_name
        self._model: SentenceTransformer | None = None

    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the model."""
        if self._model is None:
            logger.info(f"Loading sentence-transformers model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def generate_embedding(self, text: str) -> list[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Input text

        Returns:
            List of floats representing the embedding vector
        """
        if not text or not text.strip():
            # Return zero vector for empty text
            return [0.0] * 384  # MiniLM-L6-v2 produces 384-dim vectors

        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts (batch processing).

        Args:
            texts: List of input texts

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        # Filter out empty texts but keep track of indices
        valid_texts = []
        valid_indices = []
        for i, text in enumerate(texts):
            if text and text.strip():
                valid_texts.append(text)
                valid_indices.append(i)

        if not valid_texts:
            # Return zero vectors for all
            return [[0.0] * 384 for _ in texts]

        # Generate embeddings for valid texts
        embeddings = self.model.encode(valid_texts, convert_to_numpy=True)

        # Reconstruct full list with zero vectors for empty texts
        result = []
        valid_idx = 0
        for i in range(len(texts)):
            if i in valid_indices:
                result.append(embeddings[valid_idx].tolist())
                valid_idx += 1
            else:
                result.append([0.0] * 384)

        return result

    def generate_track_embedding(
        self,
        title: str,
        lyrics: str | None = None,
        themes: list[str] | None = None,
        artist_name: str | None = None,
    ) -> list[float]:
        """
        Generate a composite embedding for a track.

        Combines title, lyrics, themes, and artist name into a single
        embedding that captures the track's essence.

        Args:
            title: Track title
            lyrics: Full lyrics (optional)
            themes: List of themes (optional)
            artist_name: Artist name (optional)

        Returns:
            Embedding vector
        """
        # Build composite text
        parts = [title]

        if artist_name:
            parts.append(f"by {artist_name}")

        if themes:
            parts.append(f"themes: {', '.join(themes)}")

        if lyrics:
            # Use first 500 characters of lyrics to avoid token limits
            lyrics_excerpt = lyrics[:500]
            parts.append(lyrics_excerpt)

        composite_text = " | ".join(parts)

        return self.generate_embedding(composite_text)


def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        Cosine similarity score (0-1)
    """
    if len(vec1) != len(vec2):
        raise ValueError("Vectors must have the same dimension")

    vec1_np = np.array(vec1)
    vec2_np = np.array(vec2)

    # Compute cosine similarity
    dot_product = np.dot(vec1_np, vec2_np)
    norm1 = np.linalg.norm(vec1_np)
    norm2 = np.linalg.norm(vec2_np)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    similarity = dot_product / (norm1 * norm2)

    # Clamp to [0, 1] range
    return float(max(0.0, min(1.0, similarity)))


# Global instance (lazy loaded)
_generator: EmbeddingGenerator | None = None


def get_embedding_generator() -> EmbeddingGenerator:
    """Get the global embedding generator instance."""
    global _generator
    if _generator is None:
        _generator = EmbeddingGenerator()
    return _generator

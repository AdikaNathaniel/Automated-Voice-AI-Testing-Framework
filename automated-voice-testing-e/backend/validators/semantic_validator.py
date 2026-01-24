"""
SemanticValidator for semantic similarity validation (TASK-123).

This module provides the SemanticValidator class which validates semantic
similarity between actual and expected voice AI responses using sentence
embeddings and cosine similarity.

Key Features:
- Sentence embeddings using sentence-transformers
- Cosine similarity calculation
- Pre-trained model: all-MiniLM-L6-v2 (fast and accurate)
- Returns confidence scores (0.0 to 1.0)

Example:
    >>> from validators.semantic_validator import SemanticValidator
    >>>
    >>> # Create validator
    >>> validator = SemanticValidator()
    >>>
    >>> # Calculate similarity
    >>> actual = "Navigate to home"
    >>> expected = "Go to home"
    >>> score = validator.validate(actual, expected)
    >>> print(f"Similarity: {score:.2f}")  # ~0.85
    >>>
    >>> # Identical sentences
    >>> score = validator.validate("Play music", "Play music")
    >>> print(f"Similarity: {score:.2f}")  # ~1.0
"""

from typing import Optional
import logging
import numpy as np

logger = logging.getLogger(__name__)

# Try to import sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning("sentence-transformers not available, using fallback mode")
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None


class SemanticValidator:
    """
    Validator for semantic similarity using sentence embeddings.

    This validator uses pre-trained sentence transformer models to generate
    embeddings for text and calculates cosine similarity between them.

    The validator uses 'all-MiniLM-L6-v2' model by default, which provides:
    - Fast inference (good for real-time validation)
    - Good quality embeddings (384 dimensions)
    - Small model size (~80MB)

    Returns a confidence score from 0.0 to 1.0, where:
    - 1.0 = identical semantic meaning
    - 0.0 = completely different meaning

    Attributes:
        model: SentenceTransformer model for generating embeddings
        model_name: Name of the pre-trained model being used

    Example:
        >>> validator = SemanticValidator()
        >>>
        >>> # Validate semantic similarity
        >>> score = validator.validate(
        ...     "Navigate to home",
        ...     "Go to home"
        ... )
        >>> print(f"Similarity: {score:.2f}")
        >>>
        >>> # Get embeddings directly
        >>> embedding = validator.get_embedding("Navigate to home")
        >>> print(f"Embedding dimension: {len(embedding)}")
    """

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize SemanticValidator.

        Args:
            model_name: Name of sentence-transformers model to use.
                       Default is 'all-MiniLM-L6-v2' (fast, accurate, small)

        Example:
            >>> # Use default model
            >>> validator = SemanticValidator()
            >>>
            >>> # Use different model (larger, more accurate)
            >>> validator = SemanticValidator('all-mpnet-base-v2')
        """
        self.model_name = model_name

        if SENTENCE_TRANSFORMERS_AVAILABLE:
            logger.info(f"Loading sentence transformer model: {model_name}")
            try:
                self.model = SentenceTransformer(model_name)
                logger.info(f"Model loaded successfully: {model_name}")
            except Exception as e:
                logger.error(f"Failed to load model {model_name}: {e}")
                logger.info("Using fallback mode (exact string matching)")
                self.model = None
        else:
            logger.warning("sentence-transformers not available, using fallback mode")
            self.model = None

    def get_embedding(self, text: str) -> np.ndarray:
        """
        Generate sentence embedding for text.

        Uses the sentence transformer model to convert text into a dense
        vector representation (embedding) that captures semantic meaning.

        Args:
            text: Input text to generate embedding for

        Returns:
            numpy array containing the embedding vector

        Example:
            >>> validator = SemanticValidator()
            >>> embedding = validator.get_embedding("Navigate to home")
            >>> print(f"Embedding shape: {embedding.shape}")  # (384,)
            >>> print(f"First 5 values: {embedding[:5]}")
        """
        if self.model is None:
            # Fallback: return simple hash-based representation
            logger.warning("Using fallback embedding (model not available)")
            # Simple fallback: one-hot encoding based on hash
            text_hash = hash(text.lower().strip()) % 384
            embedding = np.zeros(384)
            embedding[text_hash] = 1.0
            return embedding

        # Generate embedding using sentence transformer
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            logger.debug(f"Generated embedding for text (length={len(text)})")
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            # Return zero vector as fallback
            return np.zeros(384)

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts.

        This method:
        1. Generates embeddings for both texts
        2. Calculates cosine similarity between embeddings
        3. Returns similarity score (0.0 to 1.0)

        Cosine similarity measures the angle between two vectors:
        - 1.0 = vectors point in same direction (very similar)
        - 0.0 = vectors are orthogonal (unrelated)
        - -1.0 = vectors point in opposite directions (opposite meaning)

        In practice, sentence embeddings rarely produce negative similarities.

        Args:
            text1: First text to compare
            text2: Second text to compare

        Returns:
            Similarity score from 0.0 to 1.0

        Example:
            >>> validator = SemanticValidator()
            >>>
            >>> # Very similar
            >>> sim = validator.calculate_similarity(
            ...     "Navigate to home",
            ...     "Go to home"
            ... )
            >>> print(f"Similarity: {sim:.2f}")  # ~0.85
            >>>
            >>> # Identical
            >>> sim = validator.calculate_similarity(
            ...     "Play music",
            ...     "Play music"
            ... )
            >>> print(f"Similarity: {sim:.2f}")  # ~1.0
            >>>
            >>> # Different
            >>> sim = validator.calculate_similarity(
            ...     "Navigate to home",
            ...     "Play loud music"
            ... )
            >>> print(f"Similarity: {sim:.2f}")  # ~0.3
        """
        # Generate embeddings
        embedding1 = self.get_embedding(text1)
        embedding2 = self.get_embedding(text2)

        # Calculate cosine similarity
        # cosine_similarity = dot(A, B) / (norm(A) * norm(B))
        try:
            dot_product = np.dot(embedding1, embedding2)
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)

            # Avoid division by zero
            if norm1 == 0 or norm2 == 0:
                logger.warning("Zero norm in embedding, returning 0.0 similarity")
                return 0.0

            cosine_sim = dot_product / (norm1 * norm2)

            # Ensure result is in valid range [0, 1]
            # Clip to handle floating point errors
            similarity = float(np.clip(cosine_sim, 0.0, 1.0))

            logger.debug(
                f"Similarity: {similarity:.3f} for texts: "
                f"'{text1[:50]}...' vs '{text2[:50]}...'"
            )

            return similarity

        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0

    def validate(
        self,
        actual: Optional[str],
        expected: Optional[str],
        threshold: Optional[float] = None
    ) -> float:
        """
        Validate semantic similarity between actual and expected text.

        This is the main validation method that calculates semantic similarity
        using sentence embeddings and cosine similarity.

        Args:
            actual: Actual text from voice AI response
            expected: Expected text to compare against
            threshold: Optional minimum similarity threshold (not used in scoring,
                      but could be used for pass/fail decisions)

        Returns:
            Confidence score from 0.0 to 1.0:
            - 1.0 = perfect semantic match
            - 0.0 = no semantic similarity

        Example:
            >>> validator = SemanticValidator()
            >>>
            >>> # High similarity
            >>> score = validator.validate(
            ...     "Navigate to home",
            ...     "Go to home"
            ... )
            >>> assert score > 0.7
            >>>
            >>> # Perfect match
            >>> score = validator.validate(
            ...     "Play music",
            ...     "Play music"
            ... )
            >>> assert score > 0.99
            >>>
            >>> # Low similarity
            >>> score = validator.validate(
            ...     "Navigate to home",
            ...     "Play loud music"
            ... )
            >>> assert score < 0.5
        """
        logger.info(
            f"Validating semantic similarity: "
            f"actual='{actual[:50] if actual else None}...', "
            f"expected='{expected[:50] if expected else None}...'"
        )

        # Handle None values
        if actual is None and expected is None:
            logger.debug("Both texts are None - returning 1.0")
            return 1.0

        if actual is None or expected is None:
            logger.debug("One text is None - returning 0.0")
            return 0.0

        # Handle empty strings
        if not actual and not expected:
            logger.debug("Both texts are empty - returning 1.0")
            return 1.0

        if not actual or not expected:
            logger.debug("One text is empty - returning 0.0")
            return 0.0

        # Calculate semantic similarity
        similarity = self.calculate_similarity(actual, expected)

        logger.info(f"Semantic similarity score: {similarity:.3f}")

        # If threshold provided, could use it for decision logic
        # For now, just return the raw similarity score
        if threshold is not None:
            logger.debug(f"Threshold: {threshold} (not used in scoring)")

        return similarity

    def __repr__(self) -> str:
        """
        String representation of SemanticValidator.

        Returns:
            String showing model name

        Example:
            >>> validator = SemanticValidator()
            >>> print(validator)
            <SemanticValidator(model='all-MiniLM-L6-v2')>
        """
        return f"<SemanticValidator(model='{self.model_name}')>"

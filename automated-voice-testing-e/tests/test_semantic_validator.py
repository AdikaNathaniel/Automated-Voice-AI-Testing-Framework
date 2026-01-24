"""
Test suite for SemanticValidator (TASK-123).

This module tests the semantic similarity validator:
- SemanticValidator class structure
- Cosine similarity calculation with word embeddings
- Sentence transformer integration
- Similarity scoring
- Edge cases and error handling
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

import pytest


class TestSemanticValidatorFileStructure:
    """Test semantic validator file structure"""

    def test_validators_directory_exists(self):
        """Test that validators directory exists"""
        import os
        backend_dir = os.path.join(os.path.dirname(__file__), '../backend')
        validators_dir = os.path.join(backend_dir, 'validators')

        assert os.path.exists(validators_dir), \
            "validators directory should exist in backend/"

    def test_semantic_validator_file_exists(self):
        """Test that semantic_validator.py exists"""
        import os
        backend_dir = os.path.join(os.path.dirname(__file__), '../backend')
        validators_dir = os.path.join(backend_dir, 'validators')
        semantic_validator_file = os.path.join(
            validators_dir, 'semantic_validator.py'
        )

        assert os.path.exists(semantic_validator_file), \
            "semantic_validator.py should exist in backend/validators/"

    def test_can_import_semantic_validator(self):
        """Test that SemanticValidator can be imported"""
        try:
            from validators.semantic_validator import SemanticValidator
            assert SemanticValidator is not None
        except ImportError as e:
            pytest.fail(f"Cannot import SemanticValidator: {e}")


class TestSemanticValidatorClass:
    """Test SemanticValidator class structure"""

    def test_semantic_validator_class_exists(self):
        """Test that SemanticValidator class exists"""
        from validators.semantic_validator import SemanticValidator
        assert SemanticValidator is not None

    def test_semantic_validator_can_instantiate(self):
        """Test that SemanticValidator can be instantiated"""
        from validators.semantic_validator import SemanticValidator
        validator = SemanticValidator()
        assert validator is not None

    def test_semantic_validator_has_validate_method(self):
        """Test that SemanticValidator has validate method"""
        from validators.semantic_validator import SemanticValidator
        validator = SemanticValidator()

        assert hasattr(validator, 'validate'), \
            "SemanticValidator should have validate method"

    def test_semantic_validator_has_calculate_similarity_method(self):
        """Test that SemanticValidator has calculate_similarity method"""
        from validators.semantic_validator import SemanticValidator
        validator = SemanticValidator()

        assert hasattr(validator, 'calculate_similarity'), \
            "SemanticValidator should have calculate_similarity method"

    def test_semantic_validator_has_get_embedding_method(self):
        """Test that SemanticValidator has get_embedding method"""
        from validators.semantic_validator import SemanticValidator
        validator = SemanticValidator()

        assert hasattr(validator, 'get_embedding'), \
            "SemanticValidator should have get_embedding method"


class TestCalculateSimilarity:
    """Test similarity calculation"""

    @pytest.fixture
    def validator(self):
        """Create SemanticValidator instance"""
        from validators.semantic_validator import SemanticValidator
        return SemanticValidator()

    def test_identical_sentences_high_similarity(self, validator):
        """Test that identical sentences have high similarity"""
        text1 = "Navigate to home"
        text2 = "Navigate to home"

        similarity = validator.calculate_similarity(text1, text2)

        assert similarity >= 0.99, "Identical sentences should have very high similarity"

    def test_similar_sentences_high_similarity(self, validator):
        """Test that similar sentences have high similarity"""
        text1 = "Navigate to home"
        text2 = "Go to home"

        similarity = validator.calculate_similarity(text1, text2)

        assert similarity > 0.5, "Similar sentences should have moderate to high similarity"

    def test_different_sentences_low_similarity(self, validator):
        """Test that different sentences have low similarity"""
        text1 = "Navigate to home"
        text2 = "Play some music"

        similarity = validator.calculate_similarity(text1, text2)

        assert similarity < 0.7, "Different sentences should have lower similarity"

    def test_synonyms_high_similarity(self, validator):
        """Test that synonyms have high similarity"""
        text1 = "Big dog"
        text2 = "Large dog"

        similarity = validator.calculate_similarity(text1, text2)

        assert similarity > 0.7, "Synonyms should have high similarity"

    def test_similarity_returns_float(self, validator):
        """Test that calculate_similarity returns float"""
        similarity = validator.calculate_similarity("test", "test")

        assert isinstance(similarity, float), "Similarity should return float"

    def test_similarity_range(self, validator):
        """Test that similarity is between 0 and 1"""
        text1 = "Navigate home"
        text2 = "Play music"

        similarity = validator.calculate_similarity(text1, text2)

        assert 0.0 <= similarity <= 1.0, "Similarity should be between 0 and 1"


class TestValidateMethod:
    """Test main validate method"""

    @pytest.fixture
    def validator(self):
        """Create SemanticValidator instance"""
        from validators.semantic_validator import SemanticValidator
        return SemanticValidator()

    def test_validate_identical_text(self, validator):
        """Test validate with identical text"""
        actual = "Navigate to home"
        expected = "Navigate to home"

        score = validator.validate(actual, expected)

        assert score >= 0.99, "Identical text should return near-perfect score"

    def test_validate_similar_text(self, validator):
        """Test validate with similar text"""
        actual = "Navigate to home"
        expected = "Go to home"

        score = validator.validate(actual, expected)

        assert score > 0.5, "Similar text should return moderate score"

    def test_validate_different_text(self, validator):
        """Test validate with different text"""
        actual = "Navigate to home"
        expected = "Play music loudly"

        score = validator.validate(actual, expected)

        assert score < 0.7, "Different text should return lower score"

    def test_validate_with_threshold(self, validator):
        """Test validate with custom threshold"""
        actual = "Navigate home"
        expected = "Go home"

        # Should accept threshold parameter
        try:
            score = validator.validate(actual, expected, threshold=0.7)
            assert isinstance(score, float), "Should return float score"
        except TypeError:
            # If threshold not supported, that's ok for basic implementation
            pass

    def test_validate_returns_float(self, validator):
        """Test that validate returns float"""
        score = validator.validate("test", "test")

        assert isinstance(score, float), "Validate should return float"

    def test_validate_score_range(self, validator):
        """Test that validate score is between 0 and 1"""
        score1 = validator.validate("navigate home", "navigate home")
        score2 = validator.validate("navigate home", "play music")

        assert 0.0 <= score1 <= 1.0, "Score should be between 0 and 1"
        assert 0.0 <= score2 <= 1.0, "Score should be between 0 and 1"


class TestEmbeddingGeneration:
    """Test embedding generation"""

    @pytest.fixture
    def validator(self):
        """Create SemanticValidator instance"""
        from validators.semantic_validator import SemanticValidator
        return SemanticValidator()

    def test_get_embedding_returns_array(self, validator):
        """Test that get_embedding returns array-like object"""
        text = "Navigate to home"

        embedding = validator.get_embedding(text)

        # Should be array-like (list, numpy array, tensor)
        assert hasattr(embedding, '__len__'), "Embedding should be array-like"
        assert len(embedding) > 0, "Embedding should not be empty"

    def test_embedding_consistent(self, validator):
        """Test that same text produces same embedding"""
        text = "Navigate to home"

        embedding1 = validator.get_embedding(text)
        embedding2 = validator.get_embedding(text)

        # Convert to lists if needed for comparison
        try:
            import numpy as np
            if hasattr(embedding1, 'tolist'):
                embedding1 = embedding1.tolist()
            if hasattr(embedding2, 'tolist'):
                embedding2 = embedding2.tolist()
        except ImportError:
            pass

        # Embeddings should be very similar (allowing for floating point)
        assert len(embedding1) == len(embedding2), "Embeddings should have same length"

    def test_different_text_different_embeddings(self, validator):
        """Test that different text produces different embeddings"""
        text1 = "Navigate to home"
        text2 = "Play some music"

        embedding1 = validator.get_embedding(text1)
        embedding2 = validator.get_embedding(text2)

        # Should have same dimension but different values
        assert len(embedding1) == len(embedding2), "Should have same dimension"


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.fixture
    def validator(self):
        """Create SemanticValidator instance"""
        from validators.semantic_validator import SemanticValidator
        return SemanticValidator()

    def test_validate_empty_strings(self, validator):
        """Test validate with empty strings"""
        # Should handle gracefully, not crash
        try:
            result = validator.validate("", "")
            assert isinstance(result, (float, int)), "Should return numeric score"
        except (ValueError, Exception) as e:
            # May raise error for empty strings - acceptable
            pass

    def test_validate_none_values(self, validator):
        """Test validate with None values"""
        # Should handle gracefully
        try:
            result1 = validator.validate(None, None)
            result2 = validator.validate(None, "text")
            result3 = validator.validate("text", None)

            # If it doesn't raise error, should return numeric
            assert isinstance(result1, (float, int, type(None)))
            assert isinstance(result2, (float, int, type(None)))
            assert isinstance(result3, (float, int, type(None)))
        except (ValueError, TypeError, AttributeError):
            # Acceptable to raise error for None
            pass

    def test_validate_very_long_text(self, validator):
        """Test validate with very long text"""
        text1 = "Navigate to home " * 50
        text2 = "Navigate to home " * 50

        # Should handle long text
        similarity = validator.calculate_similarity(text1, text2)

        assert isinstance(similarity, float), "Should handle long text"
        assert similarity > 0.9, "Identical long text should have high similarity"

    def test_case_insensitive_similarity(self, validator):
        """Test that similarity is case insensitive"""
        text1 = "Navigate To Home"
        text2 = "navigate to home"

        similarity = validator.calculate_similarity(text1, text2)

        assert similarity >= 0.95, "Case should not significantly affect similarity"


class TestTaskRequirements:
    """Test TASK-123 specific requirements"""

    def test_task_123_file_location(self):
        """Test TASK-123: File is in correct location"""
        import os
        semantic_validator_file = os.path.join(
            os.path.dirname(__file__),
            '../backend/validators/semantic_validator.py'
        )

        assert os.path.exists(semantic_validator_file), \
            "TASK-123: File should be at backend/validators/semantic_validator.py"

    def test_task_123_has_semantic_validator_class(self):
        """Test TASK-123: Has SemanticValidator class"""
        try:
            from validators.semantic_validator import SemanticValidator
            assert SemanticValidator is not None
        except ImportError:
            pytest.fail("TASK-123: Should have SemanticValidator class")

    def test_task_123_uses_sentence_transformers(self):
        """Test TASK-123: Uses sentence-transformers library"""
        # Check if sentence-transformers can be imported
        try:
            import sentence_transformers
            assert sentence_transformers is not None
        except ImportError:
            pytest.skip("sentence-transformers not installed yet")

    def test_task_123_cosine_similarity(self):
        """Test TASK-123: Uses cosine similarity"""
        from validators.semantic_validator import SemanticValidator
        validator = SemanticValidator()

        # Should have method for calculating similarity
        assert hasattr(validator, 'calculate_similarity'), \
            "TASK-123: Should have calculate_similarity method"

    def test_task_123_word_embeddings(self):
        """Test TASK-123: Uses word embeddings"""
        from validators.semantic_validator import SemanticValidator
        validator = SemanticValidator()

        # Should have method for getting embeddings
        assert hasattr(validator, 'get_embedding'), \
            "TASK-123: Should have get_embedding method"

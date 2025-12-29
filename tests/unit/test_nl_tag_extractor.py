"""Unit tests for NLTagExtractor service."""

from unittest.mock import MagicMock

import pytest

from src.services.nl_tag_extractor import NLTagExtractor, TagExtractionResult


class TestNLTagExtractorWithDSPy:
    """Unit tests for NLTagExtractor with DSPy inference."""

    @pytest.fixture
    def available_tags(self) -> list[str]:
        """Sample available tags for testing."""
        return ["hiking", "finance", "health", "fitness", "technology", "education"]

    @pytest.fixture
    def mock_lm(self) -> MagicMock:
        """Mock DSPy language model."""
        return MagicMock()

    def test_extract_single_tag_with_reasoning(
        self, available_tags: list[str], mock_lm: MagicMock
    ) -> None:
        """Test extraction of single tag returns reasoning from DSPy."""
        extractor = NLTagExtractor(available_tags, lm=mock_lm)

        # Mock DSPy result with reasoning
        mock_result = MagicMock()
        mock_result.top_tags = "hiking"
        mock_result.reasoning = (
            "The query mentions improving hiking habits, which directly relates to the hiking tag."
        )
        extractor.extractor = MagicMock(return_value=mock_result)

        result = extractor.extract("show me resources for hiking")

        assert result.tags == ["hiking"]
        assert result.confidence == 1.0
        assert result.ambiguous is False
        assert (
            result.reasoning
            == "The query mentions improving hiking habits, which directly relates to the hiking tag."
        )
        assert len(result.reasoning) > 0

    def test_extract_multiple_tags_with_reasoning(
        self, available_tags: list[str], mock_lm: MagicMock
    ) -> None:
        """Test extraction of multiple tags includes reasoning explaining ambiguity."""
        extractor = NLTagExtractor(available_tags, lm=mock_lm, ambiguity_threshold=0.15)

        # Mock DSPy result with multiple tags
        mock_result = MagicMock()
        mock_result.top_tags = "fitness, health"
        mock_result.reasoning = (
            "Query about exercise relates to both fitness training and general health."
        )
        extractor.extractor = MagicMock(return_value=mock_result)

        result = extractor.extract("tell me about exercise")

        assert len(result.tags) == 2
        assert "fitness" in result.tags
        assert "health" in result.tags
        assert result.confidence == 0.7
        assert result.ambiguous is False  # 0.7 > ambiguity_threshold
        assert (
            result.reasoning
            == "Query about exercise relates to both fitness training and general health."
        )

    def test_extract_filters_invalid_tags_preserves_reasoning(
        self, available_tags: list[str], mock_lm: MagicMock
    ) -> None:
        """Test that invalid tags are filtered but reasoning is preserved."""
        extractor = NLTagExtractor(available_tags, lm=mock_lm)

        # Mock DSPy result with invalid tag
        mock_result = MagicMock()
        mock_result.top_tags = "hiking, invalid_tag"
        mock_result.reasoning = "Query matches hiking and related outdoor activities."
        extractor.extractor = MagicMock(return_value=mock_result)

        result = extractor.extract("outdoor activities")

        assert result.tags == ["hiking"]  # Only valid tag
        assert result.reasoning == "Query matches hiking and related outdoor activities."

    def test_extract_no_reasoning_attribute_handled_gracefully(
        self, available_tags: list[str], mock_lm: MagicMock
    ) -> None:
        """Test that missing reasoning attribute defaults to empty string."""
        extractor = NLTagExtractor(available_tags, lm=mock_lm)

        # Mock DSPy result without reasoning attribute
        mock_result = MagicMock()
        mock_result.top_tags = "hiking"
        del mock_result.reasoning  # Ensure attribute doesn't exist
        extractor.extractor = MagicMock(return_value=mock_result)

        result = extractor.extract("hiking")

        assert result.tags == ["hiking"]
        assert result.reasoning == ""  # Should default to empty string


class TestNLTagExtractorFallback:
    """Unit tests for NLTagExtractor fallback (keyword-based) mode."""

    @pytest.fixture
    def available_tags(self) -> list[str]:
        """Sample available tags for testing."""
        return ["hiking", "finance", "health", "fitness", "technology", "education"]

    def test_fallback_extract_single_keyword_with_fallback_reasoning(
        self, available_tags: list[str]
    ) -> None:
        """Test keyword extraction returns fallback reasoning message."""
        # No LM provided = fallback mode
        extractor = NLTagExtractor(available_tags, lm=None)

        result = extractor.extract("I want to learn about hiking")

        assert result.tags == ["hiking"]
        assert result.confidence == 1.0
        assert result.ambiguous is False
        assert result.reasoning == "Keyword-based matching (fallback mode)"

    def test_fallback_extract_multiple_keywords_with_reasoning(
        self, available_tags: list[str]
    ) -> None:
        """Test keyword extraction of multiple tags includes fallback reasoning."""
        extractor = NLTagExtractor(available_tags, lm=None)

        result = extractor.extract("I need resources for finance and health")

        assert len(result.tags) == 2
        assert "finance" in result.tags
        assert "health" in result.tags
        assert result.confidence == 0.5
        assert result.ambiguous is True
        assert result.reasoning == "Keyword-based matching (fallback mode)"

    def test_fallback_extract_no_match_empty_reasoning(self, available_tags: list[str]) -> None:
        """Test no-match scenario returns empty reasoning."""
        extractor = NLTagExtractor(available_tags, lm=None)

        result = extractor.extract("xyzzy nonsense query")

        assert result.tags == []
        assert result.confidence == 0.0
        assert result.ambiguous is False
        assert result.reasoning == ""  # No reasoning for no-match

    def test_fallback_case_insensitive_matching_preserves_reasoning(
        self, available_tags: list[str]
    ) -> None:
        """Test fallback mode is case-insensitive and includes reasoning."""
        extractor = NLTagExtractor(available_tags, lm=None)

        result = extractor.extract("I love HIKING and want to learn more")

        assert result.tags == ["hiking"]
        assert result.confidence == 1.0
        assert result.reasoning == "Keyword-based matching (fallback mode)"

    def test_fallback_whole_word_matching_with_reasoning(self, available_tags: list[str]) -> None:
        """Test fallback mode matches whole words only and provides reasoning."""
        extractor = NLTagExtractor(available_tags, lm=None)

        # "hiking" should not match "thing"
        result = extractor.extract("I want to know about everything")

        assert "hiking" not in result.tags
        # But "technology" should match if present
        result2 = extractor.extract("I love technology and innovation")
        assert "technology" in result2.tags
        assert result2.reasoning == "Keyword-based matching (fallback mode)"


class TestNLTagExtractorEdgeCases:
    """Unit tests for edge cases in tag extraction."""

    @pytest.fixture
    def available_tags(self) -> list[str]:
        """Sample available tags."""
        return ["hiking", "finance", "health"]

    def test_empty_query_returns_no_tags_no_reasoning(self, available_tags: list[str]) -> None:
        """Test empty query returns no tags and empty reasoning."""
        extractor = NLTagExtractor(available_tags, lm=None)

        result = extractor.extract("")

        assert result.tags == []
        assert result.confidence == 0.0
        assert result.reasoning == ""

    def test_whitespace_only_query_no_reasoning(self, available_tags: list[str]) -> None:
        """Test whitespace-only query returns no tags and empty reasoning."""
        extractor = NLTagExtractor(available_tags, lm=None)

        result = extractor.extract("   ")

        assert result.tags == []
        assert result.confidence == 0.0
        assert result.reasoning == ""

    def test_special_characters_in_query_with_reasoning(self, available_tags: list[str]) -> None:
        """Test special characters don't break extraction and reasoning is provided."""
        extractor = NLTagExtractor(available_tags, lm=None)

        result = extractor.extract("hiking & camping! #outdoor")

        assert "hiking" in result.tags
        assert result.reasoning == "Keyword-based matching (fallback mode)"

    def test_unicode_characters_with_reasoning(self, available_tags: list[str]) -> None:
        """Test Unicode characters are handled and reasoning is provided."""
        extractor = NLTagExtractor(available_tags, lm=None)

        result = extractor.extract("I want to learn about hiking ☀️ and health 💪")

        assert "hiking" in result.tags
        assert "health" in result.tags
        assert result.reasoning == "Keyword-based matching (fallback mode)"

    def test_very_long_query_with_reasoning(self, available_tags: list[str]) -> None:
        """Test very long queries are handled and reasoning is provided."""
        extractor = NLTagExtractor(available_tags, lm=None)

        long_query = "I am looking for resources about hiking " * 50 + "and also some finance tips"
        result = extractor.extract(long_query)

        assert "hiking" in result.tags
        assert "finance" in result.tags
        assert result.reasoning == "Keyword-based matching (fallback mode)"


class TestTagExtractionResult:
    """Unit tests for TagExtractionResult NamedTuple."""

    def test_result_has_reasoning_field(self) -> None:
        """Test that TagExtractionResult includes reasoning field."""
        result = TagExtractionResult(
            tags=["hiking"],
            confidence=0.9,
            ambiguous=False,
            reasoning="Test reasoning",
        )

        assert result.tags == ["hiking"]
        assert result.confidence == 0.9
        assert result.ambiguous is False
        assert result.reasoning == "Test reasoning"

    def test_result_can_have_empty_reasoning(self) -> None:
        """Test that reasoning can be empty string."""
        result = TagExtractionResult(
            tags=[],
            confidence=0.0,
            ambiguous=False,
            reasoning="",
        )

        assert result.reasoning == ""
        assert isinstance(result.reasoning, str)

    def test_result_immutable(self) -> None:
        """Test that TagExtractionResult is immutable (NamedTuple)."""
        result = TagExtractionResult(
            tags=["hiking"],
            confidence=0.9,
            ambiguous=False,
            reasoning="Test",
        )

        with pytest.raises(AttributeError):
            result.reasoning = "New reasoning"  # type: ignore[misc]

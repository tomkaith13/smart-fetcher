"""Natural language tag extraction service using DSPy + Ollama."""

import logging
import re
from typing import NamedTuple

import dspy

logger = logging.getLogger(__name__)


class TagExtractionResult(NamedTuple):
    """Result of tag extraction from NL query.

    Attributes:
        tags: List of extracted tags, ordered by confidence.
        confidence: Confidence score of the top tag [0,1].
        ambiguous: True if multiple tags have similar confidence.
    """

    tags: list[str]
    confidence: float
    ambiguous: bool


class NLTagExtractor:
    """Extract domain tags from natural language queries using DSPy + Ollama.

    Uses Chain-of-Thought reasoning to map natural language queries to
    known resource tags. Falls back to keyword extraction if inference unavailable.
    """

    def __init__(
        self,
        available_tags: list[str],
        lm: dspy.LM | None = None,
        ambiguity_threshold: float = 0.15,
    ) -> None:
        """Initialize the NL tag extractor.

        Args:
            available_tags: List of canonical tags from the resource store.
            lm: Optional DSPy language model; if None, uses fallback mode.
            ambiguity_threshold: Confidence difference below which tags are ambiguous.
        """
        self.available_tags = available_tags
        self.available_tags_str = ", ".join(available_tags)
        self.lm = lm
        self.ambiguity_threshold = ambiguity_threshold

        # Create DSPy signature for tag extraction if LM available
        if self.lm is not None:
            # Note: Don't call dspy.configure here in async context
            # The LM is already configured by SemanticSearchService

            class NLToTagsSignature(dspy.Signature):  # type: ignore[misc]
                """Extract relevant resource tags from natural language query.

                Analyze the query intent and identify up to 3 most relevant tags
                from the available tag set. Rank by relevance/confidence.
                """

                query: str = dspy.InputField(
                    desc="Natural language query about resources to find"
                )
                available_tags: str = dspy.InputField(
                    desc=f"Available tags: {self.available_tags_str}"
                )
                top_tags: str = dspy.OutputField(
                    desc="Top 1-3 relevant tags from available_tags, comma-separated, ranked by confidence"
                )
                reasoning: str = dspy.OutputField(
                    desc="Brief explanation of why these tags match the query"
                )

            self.extractor = dspy.ChainOfThought(NLToTagsSignature)
        else:
            self.extractor = None
            logger.warning("NLTagExtractor initialized without LM; using fallback extraction")

    def extract(self, query: str) -> TagExtractionResult:
        """Extract tags from natural language query.

        Args:
            query: Natural language query string.

        Returns:
            TagExtractionResult with extracted tags, confidence, and ambiguity flag.
        """
        # Try DSPy extraction first
        if self.extractor is not None:
            try:
                result = self.extractor(
                    query=query,
                    available_tags=self.available_tags_str,
                )

                # Parse top_tags output
                top_tags_str = result.top_tags.strip()
                extracted = [tag.strip() for tag in top_tags_str.split(",")]

                # Filter to valid tags only
                valid_tags = [tag for tag in extracted if tag in self.available_tags]

                if valid_tags:
                    # Assign synthetic confidence scores (first=highest)
                    confidence = 1.0 if len(valid_tags) == 1 else 0.7
                    ambiguous = len(valid_tags) > 1 and (1.0 - confidence) < self.ambiguity_threshold

                    logger.info(
                        f"Extracted tags for '{query}': {valid_tags} (confidence={confidence:.2f}, ambiguous={ambiguous})"
                    )
                    return TagExtractionResult(
                        tags=valid_tags,
                        confidence=confidence,
                        ambiguous=ambiguous,
                    )

            except Exception as e:
                logger.warning(f"DSPy extraction failed: {e}; falling back to keyword extraction")

        # Fallback: keyword-based extraction
        return self._keyword_extract(query)

    def _keyword_extract(self, query: str) -> TagExtractionResult:
        """Fallback keyword-based tag extraction.

        Args:
            query: Natural language query string.

        Returns:
            TagExtractionResult based on keyword matching.
        """
        query_lower = query.lower()
        # Tokenize and match against available tags
        matched_tags = []
        for tag in self.available_tags:
            # Match whole words only
            pattern = r"\b" + re.escape(tag) + r"\b"
            if re.search(pattern, query_lower):
                matched_tags.append(tag)

        if matched_tags:
            confidence = 1.0 if len(matched_tags) == 1 else 0.5
            ambiguous = len(matched_tags) > 1
            logger.info(
                f"Keyword extraction for '{query}': {matched_tags} (confidence={confidence:.2f}, ambiguous={ambiguous})"
            )
            return TagExtractionResult(
                tags=matched_tags,
                confidence=confidence,
                ambiguous=ambiguous,
            )

        # No matches
        logger.info(f"No tags extracted for query: '{query}'")
        return TagExtractionResult(
            tags=[],
            confidence=0.0,
            ambiguous=False,
        )

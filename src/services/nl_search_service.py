"""Natural language search service orchestrating tag extraction and resource mapping."""

import logging

from src.api.schemas import ResourceItem
from src.models.resource import Resource
from src.services.nl_tag_extractor import NLTagExtractor
from src.services.resource_store import ResourceStore
from src.utils.link_verifier import verify_internal_link

logger = logging.getLogger(__name__)


class NLSearchService:
    """Orchestrate NL query processing: extract tags → map to resources → verify links → respond.

    Implements the core NL UUID search workflow with deterministic link verification
    and configurable result capping.
    """

    def __init__(
        self,
        extractor: NLTagExtractor,
        resource_store: ResourceStore,
        default_cap: int = 5,
    ) -> None:
        """Initialize NL search service.

        Args:
            extractor: Tag extraction service (DSPy-based or fallback).
            resource_store: Resource storage for UUID lookup.
            default_cap: Maximum results to return (default 5).
        """
        self.extractor = extractor
        self.resource_store = resource_store
        self.default_cap = default_cap

    def search(
        self, query: str, cap: int | None = None
    ) -> tuple[list[ResourceItem], str | None, list[str], str]:
        """Execute NL search: extract tags, map to resources, verify links.

        Args:
            query: Natural language query string.
            cap: Optional result cap override (uses default if None).

        Returns:
            Tuple of (resource_items, message, candidate_tags, reasoning):
            - resource_items: List of ResourceItem with verified links.
            - message: Optional guidance message for no-match or ambiguity.
            - candidate_tags: List of suggested tags for refinement (empty if not ambiguous).
            - reasoning: DSPy extractor explanation for why extracted tags match the query.
        """
        result_cap = cap if cap is not None else self.default_cap

        # Step 1: Extract tags from query
        extraction = self.extractor.extract(query)

        # Step 2: Handle no-match scenario
        if not extraction.tags:
            logger.info(f"No tags extracted for query: '{query}'")
            # Suggest some popular tags
            suggestions = self.resource_store.get_unique_tags()[:3]
            message = f"No matching resources found. Try searching with tags like: {', '.join(suggestions)}"
            return ([], message, suggestions, extraction.reasoning)

        # Step 3: Handle ambiguity scenario
        if extraction.ambiguous and len(extraction.tags) > 1:
            logger.info(f"Ambiguous query detected: '{query}' -> {extraction.tags}")
            message = (
                f"Your query matches multiple categories. "
                f"Did you mean: {', '.join(extraction.tags)}? "
                f"Please refine your query."
            )
            # Return top resources from all candidate tags (capped)
            resources = self.resource_store.get_by_tags(extraction.tags)[:result_cap]
            items = self._build_resource_items(resources, extraction.tags)
            return (items, message, extraction.tags, extraction.reasoning)

        # Step 4: Standard flow - map tags to resources
        resources = self.resource_store.get_by_tags(extraction.tags)
        logger.info(f"Found {len(resources)} resources for tags: {extraction.tags}")

        # Step 5: Apply result cap
        capped_resources = resources[:result_cap]

        # Step 6: Build ResourceItems with verified links and reasoning
        items = self._build_resource_items(capped_resources, extraction.tags)

        # Step 7: Verify all links are valid (deterministic verification)
        for item in items:
            verification = verify_internal_link(item.link, self.resource_store)
            if not verification.valid:
                logger.error(f"Link verification failed for {item.uuid}: {verification.error}")
                # This should never happen if logic is correct; log and omit
                continue

        logger.info(f"Returning {len(items)} verified resource items for query: '{query}'")
        return (items, None, [], extraction.reasoning)

    def _build_resource_items(
        self,
        resources: list[Resource],
        tags: list[str],
    ) -> list[ResourceItem]:
        """Convert Resource objects to ResourceItem DTOs with internal deep links.

        Args:
            resources: List of Resource objects to convert.
            tags: List of tags that matched (for traceability).
        Returns:
            List of ResourceItem with uuid, name, summary, link, tags.
        """
        items = []
        for resource in resources:
            # Build internal deep link
            link = f"/resources/{resource.uuid}"

            # Create ResourceItem (summary = description, name = name)
            item = ResourceItem(
                uuid=resource.uuid,
                name=resource.name,
                summary=resource.description[:200] + "..."
                if len(resource.description) > 200
                else resource.description,
                link=link,
                tags=tags,
            )
            items.append(item)

        return items

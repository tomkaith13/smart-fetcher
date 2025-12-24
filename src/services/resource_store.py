"""In-memory resource storage with deterministic generation."""

import random
import uuid as uuid_lib

from faker import Faker

from src.models.resource import Resource

# Seed for deterministic resource generation
SEED = 42

# 15 diverse categories for meaningful semantic search testing
TAG_CATEGORIES = [
    "home",  # -> house, residence, dwelling, apartment
    "car",  # -> automobile, vehicle, transport
    "technology",  # -> tech, digital, electronics, computing
    "food",  # -> cuisine, meal, dining, nutrition
    "health",  # -> wellness, medical, fitness, healthcare
    "finance",  # -> money, banking, investment, economy
    "travel",  # -> trip, journey, vacation, tourism
    "education",  # -> learning, school, academic, training
    "sports",  # -> athletics, fitness, recreation, games
    "music",  # -> audio, sound, entertainment, concert
    "fashion",  # -> clothing, apparel, style, wardrobe
    "nature",  # -> environment, outdoors, wildlife, ecology
    "work",  # -> job, career, employment, office
    "family",  # -> relatives, household, domestic, kinship
    "art",  # -> creative, design, visual, artistic
]


def generate_resources(count: int = 100) -> list[Resource]:
    """Generate deterministic resources using Faker with a fixed seed.

    Args:
        count: Number of resources to generate (default 100).

    Returns:
        List of Resource objects with realistic names, descriptions, and tags.
    """
    # Set seeds for reproducibility
    random.seed(SEED)
    Faker.seed(SEED)
    fake = Faker()
    fake.seed_instance(SEED)

    resources: list[Resource] = []
    for _ in range(count):
        # Use seeded random for UUID generation
        resource_uuid = str(uuid_lib.UUID(int=random.getrandbits(128)))
        resources.append(
            Resource(
                uuid=resource_uuid,
                name=fake.catch_phrase(),
                description=fake.paragraph(nb_sentences=2),
                search_tag=random.choice(TAG_CATEGORIES),
            )
        )
    return resources


class ResourceStore:
    """In-memory storage for resources with O(1) lookup by UUID.

    Attributes:
        _resources: Primary storage dict mapping UUID to Resource.
        _tags_to_uuids: Secondary index mapping tag to set of UUIDs.
        _unique_tags: List of unique tags in the store.
    """

    def __init__(self, resources: list[Resource] | None = None) -> None:
        """Initialize the store with optional pre-generated resources.

        Args:
            resources: List of resources to populate the store. If None,
                      generates 100 deterministic resources.
        """
        self._resources: dict[str, Resource] = {}
        self._tags_to_uuids: dict[str, set[str]] = {}

        if resources is None:
            resources = generate_resources()

        for resource in resources:
            self._resources[resource.uuid] = resource
            if resource.search_tag not in self._tags_to_uuids:
                self._tags_to_uuids[resource.search_tag] = set()
            self._tags_to_uuids[resource.search_tag].add(resource.uuid)

        self._unique_tags = list(self._tags_to_uuids.keys())

    def get_by_uuid(self, uuid: str) -> Resource | None:
        """Retrieve a resource by its UUID.

        Args:
            uuid: The UUID of the resource to retrieve.

        Returns:
            The Resource if found, None otherwise.
        """
        return self._resources.get(uuid)

    def get_all(self) -> list[Resource]:
        """Retrieve all resources in the store.

        Returns:
            List of all Resource objects.
        """
        return list(self._resources.values())

    def get_unique_tags(self) -> list[str]:
        """Get all unique tags in the store.

        Returns:
            List of unique tag strings.
        """
        return self._unique_tags.copy()

    def get_by_uuids(self, uuids: list[str]) -> list[Resource]:
        """Retrieve multiple resources by their UUIDs.

        Args:
            uuids: List of UUIDs to retrieve.

        Returns:
            List of found Resource objects (missing UUIDs are skipped).
        """
        return [self._resources[uuid] for uuid in uuids if uuid in self._resources]

    def count(self) -> int:
        """Get the total number of resources in the store.

        Returns:
            Number of resources.
        """
        return len(self._resources)

    def get_resources_context(self) -> list[dict[str, str]]:
        """Get a simplified context of all resources for LLM inference.

        Returns:
            List of dicts with uuid and tag for each resource.
        """
        return [{"uuid": r.uuid, "tag": r.search_tag} for r in self._resources.values()]

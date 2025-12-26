"""In-memory resource storage with deterministic generation."""

import random
import uuid as uuid_lib
from collections.abc import Callable

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

# Type alias for tag-specific content generators
TagContentGenerator = Callable[[Faker], dict[str, str]]

# Tag-specific content generators for contextually appropriate resource data
TAG_CONTENT_GENERATORS: dict[str, TagContentGenerator] = {
    "home": lambda fake: {
        "name": f"{fake.street_name()} {random.choice(['House', 'Residence', 'Property', 'Home', 'Estate'])}",
        "description": f"Located at {fake.address()}. Features {fake.catch_phrase().lower()}.",
    },
    "car": lambda fake: {
        "name": f"{fake.color()} {random.choice(['Sedan', 'SUV', 'Coupe', 'Truck', 'Hatchback', 'Convertible'])}",
        "description": f"{fake.company()} vehicle with {fake.bs()} technology. {fake.catch_phrase()}.",
    },
    "technology": lambda fake: {
        "name": f"{random.choice(['Smart', 'Digital', 'Cloud', 'AI', 'IoT', 'Quantum'])} {random.choice(['Device', 'Platform', 'System', 'Solution'])}",
        "description": f"{fake.company()} technology that {fake.bs()}. {fake.catch_phrase()}.",
    },
    "food": lambda fake: {
        "name": f"{random.choice(['Gourmet', 'Fresh', 'Organic', 'Artisan', 'Delicious'])} {random.choice(['Meal', 'Dish', 'Cuisine', 'Delight', 'Feast'])}",
        "description": f"{fake.sentence(nb_words=6)} Prepared with {fake.word()} ingredients.",
    },
    "health": lambda fake: {
        "name": f"{random.choice(['Wellness', 'Health', 'Fitness', 'Medical', 'Vitality'])} {random.choice(['Program', 'Service', 'Solution', 'Plan', 'Care'])}",
        "description": f"Professional {random.choice(['healthcare', 'wellness', 'medical', 'fitness'])} service. {fake.paragraph(nb_sentences=1)}",
    },
    "finance": lambda fake: {
        "name": f"{fake.company()} {random.choice(['Investment', 'Banking', 'Financial', 'Capital', 'Wealth'])} {random.choice(['Services', 'Solutions', 'Management'])}",
        "description": f"Financial services that {fake.bs()}. Expert {random.choice(['investment', 'banking', 'advisory'])} solutions.",
    },
    "travel": lambda fake: {
        "name": f"{fake.city()} {random.choice(['Journey', 'Adventure', 'Tour', 'Vacation', 'Trip', 'Getaway'])}",
        "description": f"Explore {fake.country()} with our exclusive travel package. {fake.catch_phrase()}.",
    },
    "education": lambda fake: {
        "name": f"{random.choice(['Academic', 'Professional', 'Advanced', 'Online', 'Executive'])} {random.choice(['Course', 'Program', 'Training', 'Certification', 'Workshop'])}",
        "description": f"Learn {fake.job().lower()} skills. {fake.sentence(nb_words=8)}",
    },
    "sports": lambda fake: {
        "name": f"{random.choice(['Elite', 'Professional', 'Amateur', 'Competitive', 'Recreational'])} {random.choice(['Athletics', 'Training', 'League', 'Competition', 'Tournament'])}",
        "description": f"{random.choice(['Athletic', 'Sports', 'Competition', 'Training'])} program. {fake.sentence(nb_words=8)}",
    },
    "music": lambda fake: {
        "name": f"{random.choice(['Live', 'Studio', 'Concert', 'Jazz', 'Rock', 'Classical'])} {random.choice(['Performance', 'Album', 'Concert', 'Collection', 'Experience'])}",
        "description": f"{random.choice(['Musical', 'Audio', 'Sound'])} entertainment featuring {fake.word()} arrangements. {fake.catch_phrase()}.",
    },
    "fashion": lambda fake: {
        "name": f"{fake.color()} {random.choice(['Designer', 'Casual', 'Formal', 'Trendy', 'Elegant', 'Modern'])} {random.choice(['Collection', 'Apparel', 'Wear', 'Fashion', 'Style'])}",
        "description": f"Stylish {random.choice(['clothing', 'apparel', 'fashion'])} line. {fake.sentence(nb_words=7)}",
    },
    "nature": lambda fake: {
        "name": f"{random.choice(['Natural', 'Wild', 'Scenic', 'Ecological', 'Green', 'Pristine'])} {random.choice(['Environment', 'Landscape', 'Habitat', 'Reserve', 'Paradise'])}",
        "description": f"{random.choice(['Natural', 'Outdoor', 'Wildlife', 'Ecological'])} experience. {fake.sentence(nb_words=8)}",
    },
}


def generate_resources(count: int = 500, seed: int = SEED) -> list[Resource]:
    """Generate deterministic resources with contextual content per tag.

    Expands dataset from 100 to 500 resources with strict single-tag categorization.
    For count=500, uses 12 of 15 available tags with minimum 40 entries per tag.
    For smaller counts, distributes evenly across 12 tags.

    Args:
        count: Number of resources to generate (default 500).
        seed: Random seed for deterministic generation (default SEED).

    Returns:
        List of Resource objects with tag-specific contextual content.
    """
    # Set seeds for reproducibility
    random.seed(seed)
    Faker.seed(seed)
    fake = Faker()
    fake.seed_instance(seed)

    # Select 12 tags for consistency
    selected_tags = TAG_CATEGORIES[:12]

    # Calculate distribution based on count
    if count >= 480:
        # For 500+: base 40 per tag, distribute remainder
        distribution: dict[str, int] = {tag: 40 for tag in selected_tags}
        remainder = count - (len(selected_tags) * 40)
        if remainder > 0:
            for i in range(remainder):
                tag = selected_tags[i % len(selected_tags)]
                distribution[tag] += 1
    else:
        # For smaller counts: distribute evenly
        base_per_tag = count // len(selected_tags)
        remainder = count % len(selected_tags)
        distribution = {tag: base_per_tag for tag in selected_tags}
        for i in range(remainder):
            distribution[selected_tags[i]] += 1

    # Generate resources with tag-specific content
    resources: list[Resource] = []
    for tag, tag_count in distribution.items():
        generator = TAG_CONTENT_GENERATORS[tag]
        for _ in range(tag_count):
            content = generator(fake)
            resource_uuid = str(uuid_lib.UUID(int=random.getrandbits(128)))
            resources.append(
                Resource(
                    uuid=resource_uuid,
                    name=content["name"],
                    description=content["description"],
                    search_tag=tag,
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
                      generates 500 deterministic resources.
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

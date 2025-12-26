"""Unit tests for ResourceStore."""

import pytest

from src.models.resource import Resource
from src.services.resource_store import (
    TAG_CATEGORIES,
    ResourceStore,
    generate_resources,
)


class TestGenerateResources:
    """Tests for the generate_resources function."""

    def test_generates_correct_count(self) -> None:
        """Test that generate_resources creates the specified number of resources."""
        resources = generate_resources(count=10)
        assert len(resources) == 10

    def test_default_count_is_500(self) -> None:
        """Test that default count is 500 resources."""
        resources = generate_resources()
        assert len(resources) == 500

    def test_resources_are_deterministic(self) -> None:
        """Test that same seed produces same resources."""
        resources1 = generate_resources(count=10)
        resources2 = generate_resources(count=10)

        for r1, r2 in zip(resources1, resources2, strict=True):
            assert r1.uuid == r2.uuid
            assert r1.name == r2.name
            assert r1.description == r2.description
            assert r1.search_tag == r2.search_tag

    def test_resources_have_valid_structure(self) -> None:
        """Test that each resource has required fields."""
        resources = generate_resources(count=5)

        for resource in resources:
            assert isinstance(resource, Resource)
            assert len(resource.uuid) == 36  # UUID v4 format
            assert len(resource.name) > 0
            assert len(resource.description) > 0
            assert resource.search_tag in TAG_CATEGORIES

    def test_resources_have_unique_uuids(self) -> None:
        """Test that all resources have unique UUIDs."""
        resources = generate_resources(count=500)
        uuids = [r.uuid for r in resources]
        assert len(uuids) == len(set(uuids))

    def test_tag_distribution_meets_minimum(self) -> None:
        """Test that each tag has at least 40 entries in 500-resource dataset."""
        from collections import Counter

        resources = generate_resources(count=500)
        tag_counts = Counter(r.search_tag for r in resources)

        # Verify each of the 12 used tags has at least 40 entries
        for tag, count in tag_counts.items():
            assert count >= 40, f"Tag '{tag}' has only {count} entries, expected ≥40"

        # Verify we're using exactly 12 tags
        assert len(tag_counts) == 12


class TestResourceStore:
    """Tests for the ResourceStore class."""

    @pytest.fixture
    def sample_resources(self) -> list[Resource]:
        """Create sample resources for testing."""
        return [
            Resource(
                uuid="550e8400-e29b-41d4-a716-446655440001",
                name="Test Resource 1",
                description="Description 1",
                search_tag="home",
            ),
            Resource(
                uuid="550e8400-e29b-41d4-a716-446655440002",
                name="Test Resource 2",
                description="Description 2",
                search_tag="car",
            ),
            Resource(
                uuid="550e8400-e29b-41d4-a716-446655440003",
                name="Test Resource 3",
                description="Description 3",
                search_tag="home",
            ),
        ]

    @pytest.fixture
    def store(self, sample_resources: list[Resource]) -> ResourceStore:
        """Create a ResourceStore with sample resources."""
        return ResourceStore(resources=sample_resources)

    def test_get_by_uuid_returns_resource(self, store: ResourceStore) -> None:
        """Test O(1) lookup by UUID returns correct resource."""
        resource = store.get_by_uuid("550e8400-e29b-41d4-a716-446655440001")

        assert resource is not None
        assert resource.name == "Test Resource 1"

    def test_get_by_uuid_returns_none_for_missing(self, store: ResourceStore) -> None:
        """Test get_by_uuid returns None for non-existent UUID."""
        resource = store.get_by_uuid("00000000-0000-0000-0000-000000000000")

        assert resource is None

    def test_get_by_uuid_returns_none_for_invalid_format(self, store: ResourceStore) -> None:
        """Test get_by_uuid returns None for invalid UUID format."""
        resource = store.get_by_uuid("not-a-uuid")

        assert resource is None

    def test_get_all_returns_all_resources(self, store: ResourceStore) -> None:
        """Test get_all returns all resources in store."""
        resources = store.get_all()

        assert len(resources) == 3

    def test_get_unique_tags_returns_tags(self, store: ResourceStore) -> None:
        """Test get_unique_tags returns all unique tags."""
        tags = store.get_unique_tags()

        assert set(tags) == {"home", "car"}

    def test_get_by_uuids_returns_matching(self, store: ResourceStore) -> None:
        """Test get_by_uuids returns resources for valid UUIDs."""
        resources = store.get_by_uuids(
            [
                "550e8400-e29b-41d4-a716-446655440001",
                "550e8400-e29b-41d4-a716-446655440002",
            ]
        )

        assert len(resources) == 2

    def test_get_by_uuids_skips_invalid(self, store: ResourceStore) -> None:
        """Test get_by_uuids skips non-existent UUIDs."""
        resources = store.get_by_uuids(
            [
                "550e8400-e29b-41d4-a716-446655440001",
                "00000000-0000-0000-0000-000000000000",
            ]
        )

        assert len(resources) == 1

    def test_get_by_tag_returns_matching(self, store: ResourceStore) -> None:
        """Test get_by_tag returns all resources with specified tag."""
        resources = store.get_by_tag("home")

        assert len(resources) == 2
        assert all(r.search_tag == "home" for r in resources)

    def test_get_by_tag_returns_empty_for_nonexistent(self, store: ResourceStore) -> None:
        """Test get_by_tag returns empty list for non-existent tag."""
        resources = store.get_by_tag("nonexistent")

        assert resources == []

    def test_count_returns_correct_number(self, store: ResourceStore) -> None:
        """Test count returns total number of resources."""
        assert store.count() == 3

    def test_get_resources_context_structure(self, store: ResourceStore) -> None:
        """Test get_resources_context returns correct format."""
        context = store.get_resources_context()

        assert len(context) == 3
        for item in context:
            assert "uuid" in item
            assert "tag" in item

    def test_default_initialization_generates_500_resources(self) -> None:
        """Test that initializing without resources generates 500."""
        store = ResourceStore()

        assert store.count() == 500

    def test_tags_to_uuids_index_correct(self, store: ResourceStore) -> None:
        """Test that tags are correctly indexed to UUIDs."""
        # 'home' should have 2 resources
        assert len(store._tags_to_uuids.get("home", set())) == 2
        # 'car' should have 1 resource
        assert len(store._tags_to_uuids.get("car", set())) == 1

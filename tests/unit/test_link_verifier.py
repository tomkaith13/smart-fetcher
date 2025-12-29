"""Unit tests for LinkVerifier."""

import uuid

import pytest

from src.models.resource import Resource
from src.services.resource_store import ResourceStore
from src.utils.link_verifier import LinkVerifier, verify_internal_link


@pytest.fixture
def resource_store() -> ResourceStore:
    """Create a resource store with test data."""
    # Create test resources with known UUIDs
    resource1 = Resource(
        uuid=str(uuid.uuid4()),
        name="Test Resource 1",
        description="This is a test resource for validation",
        search_tag="test",
    )
    resource2 = Resource(
        uuid=str(uuid.uuid4()),
        name="Test Resource 2",
        description="Another test resource for validation",
        search_tag="test",
    )
    # Initialize store with test resources
    store = ResourceStore(resources=[resource1, resource2])
    return store


def test_verify_internal_link_valid(resource_store: ResourceStore) -> None:
    """Test verify_internal_link with valid UUID that exists in store."""
    # Get a real UUID from the store
    all_resources = resource_store.get_all()
    test_uuid = all_resources[0].uuid
    link = f"/resources/{test_uuid}"

    result = verify_internal_link(link, resource_store)

    assert result.valid is True
    assert result.uuid == test_uuid
    assert result.error is None


def test_verify_internal_link_invalid_format() -> None:
    """Test verify_internal_link with invalid format."""
    store = ResourceStore()
    link = "/resources/not-a-uuid"

    result = verify_internal_link(link, store)

    assert result.valid is False
    assert result.uuid is None
    assert "Invalid UUID format" in result.error


def test_verify_internal_link_wrong_prefix() -> None:
    """Test verify_internal_link with wrong prefix."""
    store = ResourceStore()
    link = "/wrong/12345678-1234-1234-1234-123456789abc"

    result = verify_internal_link(link, store)

    assert result.valid is False
    assert result.uuid is None
    assert "must start with /resources/" in result.error


def test_verify_internal_link_uuid_not_found() -> None:
    """Test verify_internal_link with valid UUID format but not in store."""
    store = ResourceStore()
    # Valid UUID format but doesn't exist in empty store
    link = "/resources/12345678-1234-1234-1234-123456789abc"

    result = verify_internal_link(link, store)

    assert result.valid is False
    assert result.uuid == "12345678-1234-1234-1234-123456789abc"
    assert "UUID not found in resource store" in result.error


def test_link_verifier_with_resource_store(resource_store: ResourceStore) -> None:
    """Test LinkVerifier.verify_link with ResourceStore - checks existence."""
    verifier = LinkVerifier(resource_store=resource_store)

    # Get a real UUID from the store
    all_resources = resource_store.get_all()
    test_uuid = all_resources[0].uuid
    link = f"/resources/{test_uuid}"

    # Should return True for existing resource
    assert verifier.verify_link(link) is True

    # Should return False for non-existent UUID (valid format but not in store)
    fake_link = "/resources/12345678-1234-1234-1234-123456789abc"
    assert verifier.verify_link(fake_link) is False


def test_link_verifier_without_resource_store() -> None:
    """Test LinkVerifier.verify_link without ResourceStore - only format check."""
    verifier = LinkVerifier()  # No resource_store

    # Valid UUID format should pass (even if not in any store)
    valid_link = "/resources/12345678-1234-1234-1234-123456789abc"
    assert verifier.verify_link(valid_link) is True

    # Invalid UUID format should fail
    invalid_link = "/resources/not-a-uuid"
    assert verifier.verify_link(invalid_link) is False


def test_link_verifier_external_urls() -> None:
    """Test LinkVerifier with external URLs."""
    verifier = LinkVerifier()

    # HTTP/HTTPS URLs should be valid
    assert verifier.verify_link("http://example.com") is True
    assert verifier.verify_link("https://example.com/path") is True

    # Other protocols should be invalid
    assert verifier.verify_link("ftp://example.com") is False
    assert verifier.verify_link("file:///path") is False
    assert verifier.verify_link("not-a-url") is False


def test_link_verifier_with_store_external_urls(resource_store: ResourceStore) -> None:
    """Test that external URL validation doesn't require resource store."""
    verifier = LinkVerifier(resource_store=resource_store)

    # External URLs should work regardless of resource_store
    assert verifier.verify_link("https://example.com") is True
    assert verifier.verify_link("http://example.com") is True

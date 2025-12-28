"""Link verification utility for internal deep links."""

import re
from typing import NamedTuple

from src.services.resource_store import ResourceStore

# UUID regex pattern
UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


class LinkVerificationResult(NamedTuple):
    """Result of link verification.

    Attributes:
        valid: True if link is valid and resolves to an existing resource.
        uuid: Extracted UUID from the link if valid, else None.
        error: Error message if invalid, else None.
    """

    valid: bool
    uuid: str | None
    error: str | None


def verify_internal_link(link: str, resource_store: ResourceStore) -> LinkVerificationResult:
    """Verify that an internal deep link is valid and resolves to an existing resource.

    Args:
        link: Internal deep link of the form /resources/{uuid}.
        resource_store: ResourceStore to check UUID existence.

    Returns:
        LinkVerificationResult indicating validity and extracted UUID.
    """
    # Check format: must start with /resources/
    if not link.startswith("/resources/"):
        return LinkVerificationResult(
            valid=False,
            uuid=None,
            error=f"Link must start with /resources/, got: {link}",
        )

    # Extract UUID part
    uuid_part = link[len("/resources/") :]

    # Validate UUID format
    if not UUID_PATTERN.match(uuid_part):
        return LinkVerificationResult(
            valid=False,
            uuid=None,
            error=f"Invalid UUID format: {uuid_part}",
        )

    # Check if UUID exists in resource store
    resource = resource_store.get_by_uuid(uuid_part)
    if resource is None:
        return LinkVerificationResult(
            valid=False,
            uuid=uuid_part,
            error=f"UUID not found in resource store: {uuid_part}",
        )

    # All checks passed
    return LinkVerificationResult(
        valid=True,
        uuid=uuid_part,
        error=None,
    )

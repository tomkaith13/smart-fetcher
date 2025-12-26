"""Dataset validation utilities for resource integrity checks."""

from pydantic import BaseModel

from src.models.resource import Resource


class ValidationReport(BaseModel):
    """Structured validation results for dataset integrity checks.

    Attributes:
        total_count_pass: Whether total count matches expected (500).
        actual_count: Actual number of resources.
        expected_count: Expected number (500).
        tag_distribution: Per-tag validation: tag → (pass ≥40, actual count).
        unique_uuids: Whether all UUIDs are unique.
        single_tags: Whether all resources have exactly one tag.
        schema_valid: Whether all resources match Resource model.
        overall_pass: Combined pass/fail status.
    """

    total_count_pass: bool
    actual_count: int
    expected_count: int
    tag_distribution: dict[str, tuple[bool, int]]
    unique_uuids: bool
    single_tags: bool
    schema_valid: bool
    overall_pass: bool

    def summary(self) -> str:
        """Generate human-readable summary of validation results.

        Returns:
            Multi-line string with formatted validation results.
        """
        lines = [
            f"Total Count: {'✅' if self.total_count_pass else '❌'} "
            f"({self.actual_count}/{self.expected_count})",
            f"Unique UUIDs: {'✅' if self.unique_uuids else '❌'}",
            f"Single Tags: {'✅' if self.single_tags else '❌'}",
            f"Schema Valid: {'✅' if self.schema_valid else '❌'}",
            "\nTag Distribution:",
        ]
        for tag, (passed, count) in sorted(self.tag_distribution.items()):
            status = "✅" if passed else "❌"
            lines.append(f"  {tag}: {status} ({count} resources)")
        lines.append(f"\nOverall: {'✅ PASS' if self.overall_pass else '❌ FAIL'}")
        return "\n".join(lines)


def validate_total_count(resources: list[Resource], expected: int = 500) -> tuple[bool, int]:
    """Verify exact resource count matches expected.

    Args:
        resources: List of resources to validate.
        expected: Expected count (default 500).

    Returns:
        Tuple of (pass status, actual count).
    """
    actual = len(resources)
    return (actual == expected, actual)


def validate_tag_distribution(
    resources: list[Resource], min_per_tag: int = 40
) -> dict[str, tuple[bool, int]]:
    """Check each tag has minimum required entries.

    Args:
        resources: List of resources to validate.
        min_per_tag: Minimum resources per tag (default 40).

    Returns:
        Dictionary mapping tag to (pass ≥min, actual count).
    """
    from collections import Counter

    tag_counts = Counter(r.search_tag for r in resources)
    return {tag: (count >= min_per_tag, count) for tag, count in tag_counts.items()}


def validate_unique_uuids(resources: list[Resource]) -> bool:
    """Check all UUIDs are unique.

    Args:
        resources: List of resources to validate.

    Returns:
        True if all UUIDs are unique, False otherwise.
    """
    uuids = [r.uuid for r in resources]
    return len(uuids) == len(set(uuids))


def validate_single_tags(resources: list[Resource]) -> bool:
    """Verify each resource has exactly one tag.

    Args:
        resources: List of resources to validate.

    Returns:
        True if all resources have valid single tags, False otherwise.
    """
    # Since search_tag is a string field, this validates it's not empty
    # and exists (Pydantic validation ensures it's present)
    return all(r.search_tag and isinstance(r.search_tag, str) for r in resources)


def validate_schemas(resources: list[Resource]) -> bool:
    """Verify all resources match Resource Pydantic model.

    Args:
        resources: List of resources to validate.

    Returns:
        True if all resources are valid Resource instances, False otherwise.
    """
    return all(isinstance(r, Resource) for r in resources)


def validate_comprehensive(resources: list[Resource]) -> ValidationReport:
    """Run all validation checks and return comprehensive report.

    Args:
        resources: List of resources to validate.

    Returns:
        ValidationReport with all check results aggregated.
    """
    total_count_pass, actual_count = validate_total_count(resources)
    tag_distribution = validate_tag_distribution(resources)
    unique_uuids = validate_unique_uuids(resources)
    single_tags = validate_single_tags(resources)
    schema_valid = validate_schemas(resources)

    # Overall pass requires all checks to pass
    tags_pass = all(passed for passed, _ in tag_distribution.values())
    overall_pass = all([total_count_pass, tags_pass, unique_uuids, single_tags, schema_valid])

    return ValidationReport(
        total_count_pass=total_count_pass,
        actual_count=actual_count,
        expected_count=500,
        tag_distribution=tag_distribution,
        unique_uuids=unique_uuids,
        single_tags=single_tags,
        schema_valid=schema_valid,
        overall_pass=overall_pass,
    )

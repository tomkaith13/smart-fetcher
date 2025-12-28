"""Unit tests for dataset validation utilities."""


from src.models.resource import Resource
from src.utils.dataset_validator import (
    ValidationReport,
    validate_comprehensive,
    validate_schemas,
    validate_single_tags,
    validate_tag_distribution,
    validate_total_count,
    validate_unique_uuids,
)


class TestValidationReport:
    """Tests for ValidationReport model."""

    def test_summary_generates_readable_output(self) -> None:
        """Test that summary() produces human-readable validation results."""
        report = ValidationReport(
            total_count_pass=True,
            actual_count=500,
            expected_count=500,
            tag_distribution={
                "home": (True, 42),
                "car": (True, 41),
                "technology": (False, 35),
            },
            unique_uuids=True,
            single_tags=True,
            schema_valid=True,
            overall_pass=False,
        )

        summary = report.summary()

        assert "Total Count: ✅" in summary
        assert "(500/500)" in summary
        assert "home: ✅ (42 resources)" in summary
        assert "car: ✅ (41 resources)" in summary
        assert "technology: ❌ (35 resources)" in summary
        assert "Overall: ❌ FAIL" in summary


class TestValidateTotalCount:
    """Tests for validate_total_count function."""

    def test_returns_true_when_count_matches(self) -> None:
        """Test validation passes when count matches expected."""
        resources = [
            Resource(uuid=f"uuid-{i}", name=f"R{i}", description="desc", search_tag="home")
            for i in range(500)
        ]

        passed, actual = validate_total_count(resources, expected=500)

        assert passed is True
        assert actual == 500

    def test_returns_false_when_count_differs(self) -> None:
        """Test validation fails when count doesn't match."""
        resources = [
            Resource(uuid=f"uuid-{i}", name=f"R{i}", description="desc", search_tag="home")
            for i in range(450)
        ]

        passed, actual = validate_total_count(resources, expected=500)

        assert passed is False
        assert actual == 450


class TestValidateTagDistribution:
    """Tests for validate_tag_distribution function."""

    def test_passes_when_all_tags_meet_minimum(self) -> None:
        """Test validation passes when all tags have sufficient entries."""
        resources = []
        for tag in ["home", "car", "food"]:
            resources.extend([
                Resource(uuid=f"{tag}-{i}", name="R", description="desc", search_tag=tag)
                for i in range(45)
            ])

        distribution = validate_tag_distribution(resources, min_per_tag=40)

        assert all(passed for passed, _ in distribution.values())
        assert distribution["home"] == (True, 45)
        assert distribution["car"] == (True, 45)
        assert distribution["food"] == (True, 45)

    def test_fails_when_tag_below_minimum(self) -> None:
        """Test validation fails when a tag is below minimum."""
        resources = [
            Resource(uuid=f"home-{i}", name="R", description="desc", search_tag="home")
            for i in range(45)
        ]
        resources.extend([
            Resource(uuid=f"car-{i}", name="R", description="desc", search_tag="car")
            for i in range(35)
        ])

        distribution = validate_tag_distribution(resources, min_per_tag=40)

        assert distribution["home"] == (True, 45)
        assert distribution["car"] == (False, 35)


class TestValidateUniqueUuids:
    """Tests for validate_unique_uuids function."""

    def test_passes_with_unique_uuids(self) -> None:
        """Test validation passes when all UUIDs are unique."""
        resources = [
            Resource(uuid=f"uuid-{i}", name="R", description="desc", search_tag="home")
            for i in range(100)
        ]

        assert validate_unique_uuids(resources) is True

    def test_fails_with_duplicate_uuids(self) -> None:
        """Test validation fails when UUIDs are duplicated."""
        resources = [
            Resource(uuid="duplicate", name="R1", description="desc", search_tag="home"),
            Resource(uuid="duplicate", name="R2", description="desc", search_tag="car"),
            Resource(uuid="unique", name="R3", description="desc", search_tag="food"),
        ]

        assert validate_unique_uuids(resources) is False


class TestValidateSingleTags:
    """Tests for validate_single_tags function."""

    def test_passes_with_valid_tags(self) -> None:
        """Test validation passes when all resources have single valid tags."""
        resources = [
            Resource(uuid="1", name="R", description="desc", search_tag="home"),
            Resource(uuid="2", name="R", description="desc", search_tag="car"),
        ]

        assert validate_single_tags(resources) is True


class TestValidateSchemas:
    """Tests for validate_schemas function."""

    def test_passes_with_valid_resources(self) -> None:
        """Test validation passes when all items are Resource instances."""
        resources = [
            Resource(uuid="1", name="R", description="desc", search_tag="home"),
            Resource(uuid="2", name="R", description="desc", search_tag="car"),
        ]

        assert validate_schemas(resources) is True

    def test_fails_with_non_resource_objects(self) -> None:
        """Test validation fails when list contains non-Resource objects."""
        resources = [
            Resource(uuid="1", name="R", description="desc", search_tag="home"),
            {"uuid": "2", "name": "R", "description": "desc", "search_tag": "car"},  # type: ignore
        ]

        assert validate_schemas(resources) is False  # type: ignore


class TestValidateComprehensive:
    """Tests for validate_comprehensive function."""

    def test_returns_pass_for_valid_dataset(self) -> None:
        """Test comprehensive validation passes for valid 500-resource dataset."""
        resources = []
        for i, tag in enumerate(["home", "car", "food"] * 167):  # 501 resources
            resources.append(
                Resource(
                    uuid=f"uuid-{i}",
                    name=f"Resource {i}",
                    description="Valid description",
                    search_tag=tag,
                )
            )
        resources = resources[:500]  # Exactly 500

        report = validate_comprehensive(resources)

        assert report.total_count_pass is True
        assert report.unique_uuids is True
        assert report.single_tags is True
        assert report.schema_valid is True
        assert report.overall_pass is True

    def test_returns_fail_for_invalid_count(self) -> None:
        """Test comprehensive validation fails when count is wrong."""
        resources = [
            Resource(uuid=f"uuid-{i}", name="R", description="desc", search_tag="home")
            for i in range(450)
        ]

        report = validate_comprehensive(resources)

        assert report.total_count_pass is False
        assert report.overall_pass is False

    def test_returns_fail_for_insufficient_tag_distribution(self) -> None:
        """Test comprehensive validation fails when tags below minimum."""
        resources = []
        # Create unbalanced distribution with one tag below minimum
        resources.extend([
            Resource(uuid=f"home-{i}", name="R", description="desc", search_tag="home")
            for i in range(465)
        ])
        resources.extend([
            Resource(uuid=f"car-{i}", name="R", description="desc", search_tag="car")
            for i in range(35)  # Below minimum of 40
        ])

        report = validate_comprehensive(resources)

        assert report.total_count_pass is True
        assert report.tag_distribution["car"][0] is False  # car tag fails
        assert report.overall_pass is False  # Overall fails due to car tag

    def test_comprehensive_includes_all_checks(self) -> None:
        """Test comprehensive validation includes all validation checks."""
        resources = [
            Resource(uuid="1", name="R", description="desc", search_tag="home")
        ]

        report = validate_comprehensive(resources)

        # Verify all fields are populated
        assert isinstance(report.total_count_pass, bool)
        assert isinstance(report.actual_count, int)
        assert isinstance(report.expected_count, int)
        assert isinstance(report.tag_distribution, dict)
        assert isinstance(report.unique_uuids, bool)
        assert isinstance(report.single_tags, bool)
        assert isinstance(report.schema_valid, bool)
        assert isinstance(report.overall_pass, bool)

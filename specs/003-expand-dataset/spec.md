# Feature Specification: Expand Dataset for Semantic Search Testing

**Feature Branch**: `003-expand-dataset`  
**Created**: December 26, 2025  
**Status**: Draft  
**Input**: User description: "a project to expand the dataset from 100 to 500. so that we add more data for searching in this initial dataset for this semantic search service. We want to expand the existing tags. We need to ensure that each tag has atleast 40 entries."

## Clarifications

### Session 2025-12-26

- Q: How are existing tags currently distributed in the 100-resource dataset? → A: Multiple distinct tags exist, some with overlap (e.g., "home", "car", "technology", "health", "finance")
- Q: What is the data source strategy for generating the 400 additional resources? → A: Generate synthetic/mock data programmatically using existing frameworks
- Q: How should resources be distributed across tags to ensure proper test coverage? → A: Each tag gets exactly 40 entries minimum, remainder distributed proportionally
- Q: Can resources have multiple tags or must they be single-tagged? → A: Each resource must have exactly one tag (strict categorization)
- Q: What is the acceptable content diversity level for synthetic data generation? → A: Varied but contextually appropriate (e.g., "home" tags get house-related content with natural variation)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Comprehensive Tag Coverage Testing (Priority: P1)

Quality assurance teams need to test the semantic search service with a sufficiently large and diverse dataset that represents realistic usage patterns. Currently, with only 100 resources, testing is limited and may not reveal edge cases or performance characteristics under typical load. Expanding to 500 resources with at least 40 entries per tag enables thorough testing of semantic matching accuracy and recall across all tag categories.

**Why this priority**: This is the foundation for meaningful testing. Without adequate test data, we cannot validate whether the semantic search service correctly identifies related concepts across different tag categories. This directly impacts the ability to assess system readiness for production use.

**Independent Test**: Can be fully tested by loading the expanded dataset into the resource store, verifying that each tag has at least 40 entries, confirming the total count is 500 resources, and validating that all resources are searchable. This delivers immediate value by enabling comprehensive search testing across all tag categories.

**Acceptance Scenarios**:

1. **Given** the resource store contains only 100 resources, **When** the dataset is expanded, **Then** the resource store must contain exactly 500 resources
2. **Given** the expanded dataset is loaded, **When** querying the count of resources per tag, **Then** each existing tag must have at least 40 associated resources
3. **Given** the expanded dataset with 500 resources, **When** performing semantic searches on any tag, **Then** the search service must return results without performance degradation compared to the 100-resource baseline

---

### User Story 2 - Diverse Semantic Relationship Testing (Priority: P2)

Developers and QA engineers need to test that the semantic search correctly identifies synonyms, related concepts, and contextual similarities across a broader range of examples. With more entries per tag, they can validate that the DSPy model consistently groups semantically related terms even when expressed in different ways or contexts.

**Why this priority**: This validates the core value proposition of semantic search - finding related concepts beyond exact matches. More data per tag means more opportunities to test synonym recognition, contextual understanding, and edge cases in semantic matching.

**Independent Test**: Can be tested by executing searches for known synonyms and related terms (e.g., searching "automobile" should match "car" tags, "residence" should match "home" tags) and measuring the precision and recall of semantic matches. Delivers value by validating the intelligence of the search system.

**Acceptance Scenarios**:

1. **Given** 40+ resources tagged with "home", **When** searching for semantically related terms like "house", "residence", or "dwelling", **Then** the system must return resources tagged with "home" with appropriate confidence
2. **Given** 40+ resources tagged with "car", **When** searching for related terms like "vehicle", "automobile", or "transportation", **Then** the system must return resources tagged with "car"
3. **Given** multiple resources with similar but distinct concepts (e.g., "laptop" vs "computer" vs "technology"), **When** performing searches, **Then** the system must demonstrate appropriate semantic boundaries between closely related concepts

---

### User Story 3 - Performance and Scalability Baseline (Priority: P3)

Operations and development teams need to establish performance baselines with realistic data volumes to understand how the semantic search service behaves as data grows. Testing with 500 resources provides a 5x increase from the current baseline, enabling measurement of response times, resource utilization, and identification of potential bottlenecks before production deployment.

**Why this priority**: While less critical than accuracy and coverage, understanding performance characteristics prevents surprises during production rollout. This data informs capacity planning and helps identify optimization opportunities.

**Independent Test**: Can be tested by executing a standardized suite of search queries against the 500-resource dataset, measuring response times, memory usage, and CPU utilization, then comparing against baselines from the 100-resource dataset. Delivers value by providing concrete performance data for capacity planning.

**Acceptance Scenarios**:

1. **Given** the expanded 500-resource dataset, **When** executing 100 consecutive search queries, **Then** the average response time must not exceed 2x the baseline response time from the 100-resource dataset
2. **Given** the system is running with 500 resources loaded, **When** monitoring memory usage during search operations, **Then** memory utilization must remain within acceptable limits defined by the deployment environment
3. **Given** multiple concurrent users performing searches on the 500-resource dataset, **When** measuring system throughput, **Then** the system must maintain acceptable response times under expected concurrent load

---

### Edge Cases

- What happens when a tag has exactly 40 entries and no more? (Boundary condition for minimum requirement)
- What happens when tags receive proportionally distributed additional entries beyond the 40 minimum? (Some tags will have more than 40 based on proportional allocation)
- How does the system handle newly added resources that reference tags from the expanded dataset?
- What happens when searching for a tag that exists in the expanded data but had no entries in the original 100-resource dataset?
- How does the strict single-tag constraint affect semantic search testing compared to multi-tag scenarios?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Dataset MUST contain exactly 500 resources after expansion
- **FR-002**: Each of 12 selected tags from the existing tag vocabulary (specifically: home, car, technology, food, health, finance, travel, education, sports, music, fashion, nature) MUST have at least 40 associated resource entries in the expanded dataset, with any remaining resources (20 total) distributed proportionally based on tag frequency in the original 100-resource baseline
- **FR-003**: Expanded resources MUST be generated programmatically using synthetic/mock data with titles and descriptions that are varied but contextually appropriate to their assigned tag. Content appropriateness is defined as: (1) using tag-specific Faker method combinations documented in data-model.md, (2) including at least 3 distinct variation patterns per tag, and (3) passing manual review of 5 random samples per tag for semantic relevance to the tag category
- **FR-004**: All expanded resources MUST follow the same schema and format as the original 100 resources (UUID, title, description, tags)
- **FR-005**: Each resource MUST have exactly one tag (strict categorization with no multi-tag resources)
- **FR-006**: Expanded dataset MUST be verifiable through programmatic validation (e.g., automated tests that count resources per tag)
- **FR-007**: Expanded dataset MUST maintain the semantic relationships and tag meanings from the original dataset
- **FR-008**: Resource UUIDs in the expanded dataset MUST be unique and not conflict with existing resource identifiers
- **FR-009**: Tags in expanded resources MUST use 12 selected tags from the existing 15-tag vocabulary (work, family, and art are excluded due to mathematical constraints: 12 tags × 40 minimum = 480, leaving 20 for proportional distribution to reach 500 total)

### Key Entities

- **Resource**: A searchable item containing a UUID, title, description, and exactly one tag. Represents the fundamental unit of data in the semantic search system. Each resource must be uniquely identifiable, contain sufficient textual content for semantic matching, and be categorized under a single tag for strict classification testing.

- **Tag**: A categorical label applied to resources to indicate their subject matter, purpose, or characteristics. Tags enable grouping of related resources and serve as the primary dimension for semantic search queries. In the expanded dataset, each tag represents a semantic concept that should have at least 40 associated resources.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Resource store contains exactly 500 resources as verified by automated count queries
- **SC-002**: 100% of the 12 selected tags have at least 40 associated resources in the expanded dataset (tags: home, car, technology, food, health, finance, travel, education, sports, music, fashion, nature)
- **SC-003**: Single-term semantic search queries executed sequentially against the full 500-resource dataset return results within 3 seconds for 95% of queries (measured on reference hardware: MacBook Pro M1 2020 or GitHub Actions ubuntu-latest runner)
- **SC-004**: QA team can execute at least 50 distinct semantic search test cases using the expanded dataset, covering all 12 tag categories with test case breakdown: synonym searches (20 cases), multi-word semantic queries (15 cases), edge cases (10 cases), and tag boundary tests (5 cases)
- **SC-005**: Data validation tests pass with 100% success rate confirming dataset integrity (unique UUIDs, proper schema compliance, tag consistency)
- **SC-006**: Semantic search precision (percentage of returned results that are actually relevant) remains at or above the baseline established with the 100-resource dataset

### Implementation Notes

**Performance Optimization** (Post-Implementation): During implementation, a semantic search optimization was identified and implemented to handle the 5x dataset increase efficiently. The service was refactored from sending all 500 resources to the LLM (UUID-selection approach) to sending only 12 unique tags (tag-classification approach). This optimization achieved 97% reduction in LLM context size while maintaining semantic search accuracy. The two-step process (classify search tag → lookup resources by tag) provides faster inference times and more predictable results, ensuring **SC-003** is easily met even as the dataset scales further. See [research.md](research.md#6-semantic-search-optimization-post-implementation) and [plan.md](plan.md#post-implementation-optimization) for technical details.

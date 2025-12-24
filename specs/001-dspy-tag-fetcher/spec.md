# Feature Specification: Smart Tag-Based Resource Fetcher

**Feature Branch**: `001-dspy-tag-fetcher`
**Created**: 2025-12-24
**Status**: Draft
**Input**: User description: "Develop a smart-fetcher application that uses DSPy (served via a FastAPI app) that takes in a search tag and pulls up the corresponding resources by a uuid. Each resource obj has the following: a uuid, a name (String) and description (string) and a search-tag (a human readable string). For now, we are going to randomly generate 100 such resources, stored in-memory, and we want the agent to fetch the corresponding resources as per the matching tag. For ex, tag: home will fetch all resources that are related to home. Look for synonyms. Finally i want this DSPy inference wrapped in a fastapi endpoint for me to call using Postman or cURL."

## Clarifications

### Session 2025-12-24

- Q: Which LLM backend will power DSPy inference? → A: Ollama with gpt-oss:20b (local)
- Q: What JSON response structure for search results? → A: Wrapped format with metadata: `{"results": [...], "count": N, "query": "tag"}`
- Q: Should resource generation be deterministic or random? → A: Deterministic with fixed seed (same 100 resources every restart)
- Q: What format for error responses? → A: Wrapped format: `{"error": "message", "code": "ERROR_CODE", "query": "..."}`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Search Resources by Tag (Priority: P1)

As a developer or API consumer, I want to search for resources using a human-readable tag so that I can find all resources semantically related to my search term, including those tagged with synonyms or related concepts.

**Why this priority**: This is the core functionality of the application. Without tag-based search with synonym matching, the application has no value. This represents the primary use case.

**Independent Test**: Can be fully tested by sending a tag query (e.g., "home") to the search endpoint and verifying that resources with related tags (e.g., "house", "residence", "dwelling") are returned.

**Acceptance Scenarios**:

1. **Given** the system has 100 pre-generated resources with various tags, **When** a user searches with tag "home", **Then** the system returns all resources whose tags are semantically related to "home" (including synonyms like "house", "residence", "dwelling")
2. **Given** the system has resources tagged with "automobile", "car", "vehicle", **When** a user searches with tag "car", **Then** all three resources are returned because they are semantically related
3. **Given** the system is running, **When** a user sends a search request with a valid tag, **Then** each returned resource includes its uuid, name, description, and original search-tag

---

### User Story 2 - Retrieve Resource by UUID (Priority: P2)

As a developer, I want to retrieve a specific resource by its unique identifier so that I can access detailed information about a resource I discovered through search.

**Why this priority**: After discovering resources via tag search, users need a way to fetch individual resources. This completes the basic resource access workflow.

**Independent Test**: Can be fully tested by requesting a specific UUID and verifying the correct resource is returned with all its attributes.

**Acceptance Scenarios**:

1. **Given** a resource exists with a specific UUID, **When** a user requests that UUID, **Then** the system returns the complete resource object (uuid, name, description, search-tag)
2. **Given** a UUID that does not exist in the system, **When** a user requests that UUID, **Then** the system returns an appropriate "not found" response

---

### User Story 3 - List All Resources (Priority: P3)

As a developer, I want to list all available resources so that I can browse the complete catalog and understand what resources exist in the system.

**Why this priority**: This is a convenience feature for discovery and debugging. The primary workflow (tag search) doesn't depend on it.

**Independent Test**: Can be fully tested by calling the list endpoint and verifying all 100 resources are returned.

**Acceptance Scenarios**:

1. **Given** the system has 100 pre-generated resources, **When** a user requests all resources, **Then** the system returns all 100 resources with their complete information

---

### Edge Cases

- What happens when a user searches with an empty tag? System returns an error indicating a tag is required.
- What happens when a user searches with a tag that has no semantic matches? System returns an empty result set.
- What happens when the search tag contains special characters? System sanitizes input and performs search on the cleaned tag.
- How does the system handle very long tag strings? System truncates or rejects tags exceeding a reasonable length (e.g., 100 characters).
- What happens when the intelligent matching service is temporarily unavailable? System returns an error with appropriate status code indicating service unavailability.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide an endpoint that accepts a search tag as input and returns matching resources
- **FR-002**: System MUST perform semantic/synonym matching when searching by tag (e.g., "home" matches "house", "residence")
- **FR-003**: System MUST return resources in a wrapped JSON format: `{"results": [{resource}, ...], "count": N, "query": "<searched-tag>"}` where each resource contains uuid, name, description, and search-tag
- **FR-004**: System MUST generate and maintain 100 resources in memory on startup using a fixed seed for deterministic, reproducible results across restarts
- **FR-005**: Each resource MUST have a unique identifier (uuid), a name, a description, and a search-tag
- **FR-006**: System MUST provide an endpoint to retrieve a single resource by its uuid
- **FR-007**: System MUST return error responses in wrapped JSON format: `{"error": "<message>", "code": "<ERROR_CODE>", "query": "<input>"}` for invalid requests (missing tag, invalid uuid, service unavailable, etc.)
- **FR-008**: System MUST be callable via standard HTTP clients (Postman, cURL, etc.)
- **FR-009**: System MUST use AI/ML-based inference for determining semantic similarity between tags

### Key Entities

- **Resource**: The primary data object representing a searchable item. Contains a unique identifier (uuid), human-readable name, descriptive text (description), and a categorization label (search-tag). Resources are generated randomly on system startup and stored in memory.
- **Search Tag**: A human-readable string used for categorizing and searching resources. Tags are matched semantically, meaning synonyms and related concepts are considered matches.
- **Search Result**: A collection of resources that match a given search tag query, including resources with semantically similar tags.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can search for resources by tag and receive results in under 3 seconds for typical queries
- **SC-002**: Synonym matching successfully identifies related resources at least 80% of the time for common English words (e.g., searching "car" finds resources tagged "automobile", "vehicle")
- **SC-003**: 100% of valid search requests return a well-formed response (success with results OR success with empty set)
- **SC-004**: Users can retrieve any individual resource by UUID in under 500 milliseconds
- **SC-005**: The system correctly generates and serves all 100 resources on startup without manual intervention

## Assumptions

- The 100 resources will have randomly generated but realistic names, descriptions, and tags (not gibberish)
- Resources and their tags will cover a variety of common categories to enable meaningful semantic search testing
- The system operates in a single-instance mode (no horizontal scaling requirements for this version)
- No authentication or authorization is required for accessing the endpoints
- The intelligent matching service will use Ollama with the gpt-oss:20b model running locally for semantic understanding
- In-memory storage is acceptable; data persistence across restarts is not required

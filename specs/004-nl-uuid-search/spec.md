# Feature Specification: Natural Language UUID Search

**Feature Branch**: `004-nl-uuid-search`  
**Created**: December 27, 2025  
**Status**: Draft  
**Input**: User description: "Implement a new service that takes in natural language query and looks up specific uuids. Refactor existing work as needed but keep the existing functionality intact. For example, if the user searches for \"show me resources that help me improve my hiking habits\", we need to extract the appropriate search tags, run the classifier, and return the results. The results should be in natural language with appropriate resource links for users to click into if needed. Ensure we do not hallucinate resource links. Use the same stack we have for inference if possible."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ask in natural language, get verified resources (Priority: P1)

Users enter a natural language query (e.g., "show me resources that help me improve my hiking habits") and receive a concise, human-friendly response listing relevant resources. The system extracts search tags from the query, maps them to known resource UUIDs, and returns only verified links sourced from the existing dataset/store—no hallucinated URLs.

**Why this priority**: This is the core value: enabling intuitive, NL-driven discovery while ensuring trustworthiness of links.

**Independent Test**: Provide a query with known tag mappings; verify that returned resources match expected UUIDs and that links are all from canonical sources.

**Acceptance Scenarios**:

1. **Given** a query that maps to existing tags (e.g., "hiking", "habits"), **When** the user submits the query, **Then** the system returns 3–5 relevant resources with titles, short descriptions, and verified links.
2. **Given** a query with multiple intents (e.g., "hiking and nutrition"), **When** the user submits the query, **Then** the system returns a blended set of resources covering both intents and does not include any unverified or fabricated URLs.

---

### User Story 2 - Transparent handling of no-match queries (Priority: P2)

If the query does not map to any known tags or UUIDs, the system provides a helpful, natural language response explaining that no verified resources were found, suggests related tags or alternative phrasing, and does not produce placeholder or fabricated links.

**Why this priority**: Maintains trust and reduces frustration; avoids hallucinations.

**Independent Test**: Use a query with no known tag mappings; verify that the response is helpful, contains no links, and suggests at least two related tags.

**Acceptance Scenarios**:

1. **Given** a query with no tags found, **When** the user submits the query, **Then** the system responds with a friendly message and suggestions without links.

---

### User Story 3 - Ambiguity handling and refinement (Priority: P3)

For ambiguous queries, the system identifies top candidate tags or categories and prompts refinement (e.g., "Did you mean hiking safety or hiking training?") while still only presenting verified options.

**Why this priority**: Improves discovery and reduces irrelevant results.

**Independent Test**: Submit an ambiguous query; verify that the system lists top 2–3 tag options and allows the user to refine the query.

**Acceptance Scenarios**:

1. **Given** an ambiguous query, **When** submitted, **Then** the system returns a short refinement prompt with candidate tags.

### Edge Cases

- Extremely long or multi-sentence queries: system should extract tags and respond within acceptable time without truncating meaning.
- Conflicting intents (e.g., "hiking" + "indoor-only"): system prioritizes highest-confidence tags and notes conflicts.
- Link verification failure: system excludes any resource lacking a canonical link and logs the omission.
- Inference pipeline temporarily unavailable: system falls back to a minimal keyword-based tag extraction and still avoids fabricating links.
- Rate-limiting of inference: system queues or returns a friendly retry message.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST accept a natural language query and extract relevant domain tags from it using the existing inference capability (classifier/extractor).
- **FR-002**: The system MUST map extracted tags to known resource UUIDs using the canonical resource store/dataset.
- **FR-003**: The system MUST generate a natural language response that includes resource titles, brief summaries, and verified links; links MUST originate from the canonical store and NEVER be fabricated.
- **FR-003 (updated)**: The system MUST generate a natural language response that includes resource titles, brief summaries, and verified links; links MUST be internal deep links of the form `/resources/{uuid}` derived from the canonical store and NEVER be fabricated.
- **FR-004**: The system MUST provide a deterministic link verification step that ensures each returned internal deep link maps to an existing UUID in the dataset/store for the associated resource.
- **FR-005**: The system MUST maintain existing search and list functionality; any refactoring MUST preserve current API responses and behavior.
- **FR-006**: The system MUST use the same existing inference stack for tag extraction/classification where available; if unavailable, MUST use a safe fallback that still prevents link hallucination.
- **FR-007**: The system MUST handle no-match queries by returning a helpful NL response with suggested tags and zero links.
- **FR-008**: The system SHOULD cap results per query to a reasonable default and allow configuration for the cap. [NEEDS CLARIFICATION: default maximum results per query]
- **FR-008 (updated)**: The system SHOULD cap results per query to 5 by default (configurable) and enforce this cap consistently across NL responses and API outputs.
- **FR-009**: The system SHOULD support ambiguity handling by returning top candidate tags and prompting refinement.
- **FR-010**: The system MUST ensure traceability from returned resources back to their UUIDs and tags for auditability.
- **FR-011**: Responses MUST be presented as a bulleted list where each item contains the resource title (name), a brief summary (description), and an internal deep link of the form `/resources/{uuid}`.

### Key Entities *(include if feature involves data)*

- **Query**: The natural language input provided by a user; attributes include raw text, extracted tags, confidence scores.
- **Tag**: Domain-specific label derived from the query; attributes include name, confidence, synonyms.
- **Resource**: Canonical item in the dataset/store; attributes include `uuid`, title, summary, canonical link(s), associated tags.
- **Mapping**: Associations between tags and resources; attributes include tag name, `uuid`, mapping confidence.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users receive a verified resource response for valid queries in under 2 seconds for 90% of requests (measured end-to-end from query submission to response).
- **SC-002**: 0% fabricated links across all responses; all links must be present in the canonical store for their associated UUIDs.
- **SC-003**: For queries with known tag mappings, at least 85% of the top-3 returned resources are judged relevant by domain acceptance tests.
- **SC-004**: For no-match queries, 100% of responses include a helpful message and at least two suggested tags; no links are included.
- **SC-005**: User satisfaction (task completion prompts) indicates 80%+ users can find a relevant resource within the first response without further refinement.

## Assumptions

- The canonical resource store contains UUIDs, titles, summaries, and at least one verified link per resource.
- The existing inference capability can extract tags and/or classify intents sufficient for mapping to resources.
- A reasonable default cap on results per query is 5 unless otherwise specified. [NEEDS CLARIFICATION: confirm default cap]
- Default results cap is 5 (configurable) and applied uniformly across responses.
- Verified links are internal deep links of the form `/resources/{uuid}` generated from the resource store; external links are excluded.
- The default response format is a bulleted list (title + brief summary + internal deep link).

## Clarifications

### Session 2025-12-27

- Q: Link type/source to include → A: Internal deep links only
- Q: Default maximum results per query → A: 5
- Q: Preferred response format for users → A: Bulleted list: title + summary + `/resources/{uuid}`

## Clarifications Needed (remaining)

1. (none)

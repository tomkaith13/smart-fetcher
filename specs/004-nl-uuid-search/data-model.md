# Data Model for Natural Language UUID Search

## Entities

- Query
  - Fields: `raw_text: str`, `extracted_tags: list[str]`, `confidence: float`, `ambiguous: bool`, `reasoning: str`
  - Validation: `raw_text` non-empty; max length 1000; confidence ∈ [0,1]
  - Notes: `ambiguous` set when multiple tags have similar confidence; `reasoning` contains DSPy explanation or empty string if unavailable.

- Tag
  - Fields: `name: str`, `confidence: float`, `synonyms: list[str]`
  - Validation: `name` non-empty; confidence ∈ [0,1]

- Resource
  - Fields: `uuid: str`, `title: str`, `summary: str`, `tags: list[str]`
  - Validation: `uuid` valid UUID; `title` non-empty; `summary` length ≤ 500; `tags` non-empty

- Reasoning
  - Fields: `text: str`, `source: str` (DSPy or fallback)
  - Validation: `text` non-empty if source is DSPy; empty string if fallback
  - Notes: Brief explanation of why extracted tags match the query

- Mapping
  - Fields: `tag: str`, `uuid: str`, `confidence: float`
  - Validation: `tag` exists in canonical tag set; `uuid` exists in `ResourceStore`; confidence ∈ [0,1]

## Relationships

- Tag ↔ Resource: many-to-many via `Mapping`
- Query → Tag: one-to-many (extracted tags with confidence)

## State Transitions

- Query Submitted → Tag Extraction →
  - If one tag high-confidence: Map to resources
  - If multiple similar-confidence: Ambiguity prompt with top tags
  - If no tags: No-match response with suggestions

## Constraints

- Result cap: 5 default (configurable), enforced post-mapping
- Links: Internal deep links only `/resources/{uuid}`; must resolve in `ResourceStore`
- Traceability: For each returned resource, keep provenance: selected tag and UUID mapping

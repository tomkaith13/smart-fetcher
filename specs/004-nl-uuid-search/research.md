# Phase 0 Research Summary

## Decisions

- Decision: Use DSPy + Ollama for NL tag extraction
  - Rationale: Aligns with existing stack; supports Chain-of-Thought for robust tag matching; minimizes new infra.
  - Alternatives considered: Keyword-only extraction (too brittle), external LLM APIs (adds latency/cost, external dependency).

- Decision: Default results cap = 5 (configurable)
  - Rationale: Matches spec clarifications; balances brevity and usefulness; helps keep responses within SC-001.
  - Alternatives considered: 3 (risk of missing relevant items), 10 (too verbose; potential latency increase).

- Decision: Internal deep links only (`/resources/{uuid}`)
  - Rationale: Guarantees link verifiability; prevents hallucination; consistent UX.
  - Alternatives considered: External links (risk fabrication), raw URLs from dataset (inconsistent client routing).

- Decision: Deterministic link verification step
  - Rationale: Ensures every returned UUID resolves in `ResourceStore`; enforces zero fabricated links (SC-002).
  - Alternatives considered: Probabilistic checks (insufficient for non-hallucination guarantee).

- Decision: Response format = bulleted list of title + summary + internal link
  - Rationale: Matches spec; improves readability; consistent across API and NL outputs.
  - Alternatives considered: Table/grid formatting (heavier), JSON-only presentation in UI.

- Decision: Add NL entrypoint (`GET /nl/search?q=`)
  - Rationale: Clean separation from existing tag-based `/search`; enables end-to-end NL handling (extract → map → respond) while preserving current API.
  - Alternatives considered: Overload existing `/search` (mixes concerns; breaks contract semantics).

## Best Practices

- Inference reliability: Early health check (connection + model loaded) with graceful fallback to keyword match if degraded; never fabricate links.
- Test strategy: Unit tests mock DSPy/Ollama; integration tests use service with fallback; contract tests validate schemas for new endpoint.
- Performance: Cache set of available tags; bound result count; avoid repeated model init; leverage startup health snapshot.

## Patterns

- Tag extraction: Chain-of-Thought classification mapping NL query to best matching tag(s).
- Ambiguity handling: Return top candidate tags and refinement prompt when confidence distribution is flat.
- No-match behavior: Friendly message, suggested related tags, zero links.

## Open Questions (resolved)

- Default cap: 5 (confirmed)
- Link type: Internal deep links only
- Response format: Bulleted list with title, summary, `/resources/{uuid}`

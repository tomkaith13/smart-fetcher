# Research: Ollama Model Health Check

## Decisions

- Decision: Perform startup-only health verification (no runtime checks)
  - Rationale: Avoids runtime dependency flakiness and overhead; aligns with operator workflow (restart to refresh)
  - Alternatives: per-request checks (higher load, flakiness), periodic background tasks (complexity, state drift)

- Decision: HTTP status codes — 200 for healthy/degraded; 503 for unhealthy
  - Rationale: Preserves monitoring body parsing for degraded while signaling hard-fail for unreachable service
  - Alternatives: Always 200; 503 for degraded as well (too aggressive)

- Decision: Backward-compatible response augmentation
  - Rationale: Add `ollama`, `ollama_message`, `model_name` while keeping existing fields `status`, `resources_loaded`
  - Alternatives: Replace fields (breaking change)

## Patterns & References

- Health endpoints commonly return 200 with body details; 503 reserved for service-unavailable states
- Startup health snapshot reduces coupling to external dependencies at request time

## Open Questions (resolved)

- How to verify model? → `ollama ps` once at startup; match base model name
- Where to store status? → `app.state.health_snapshot`
- How to expose model name? → From `SemanticSearch.model`

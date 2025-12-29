# Phase 0 Research

## Unknowns and Decisions

### LLM Provider for ReACT Agent
- Decision: Use DSPy with a local Ollama backend, default model `gpt-oss:20b`; keep provider pluggable (OpenAI-compatible as alternative).
- Rationale: DSPy provides structured tool integration, signatures, and ReACT-style programs; local dev-friendly and cost-effective. Specified `gpt-oss:20b` ensures consistent capability; pluggable design enables swapping providers without changing endpoint contract.
- Alternatives considered: Direct OpenAI-only integration (reduces local dev), rule-based only (insufficient for general NL queries).

### Authentication & User Identity for Rate Limiting
- Decision: Start with per-IP (X-Forwarded-For aware) identification for experimental endpoint; allow injection of user ID via header (e.g., `X-User-Id`) if available.
- Rationale: Simple to implement, works without auth infra; supports future integration with real auth.
- Alternatives considered: JWT-based auth (requires infra), session tokens (adds complexity), unauthenticated and no identity (breaks per-user rate limiting).

### Logging of Tool Actions
- Decision: Structured in-memory and file-based logs for development; define a simple JSON line format with `timestamp`, `agent_session_id`, `tool`, `params`, `result_summary`.
- Rationale: Auditable for debugging and iteration; simple implementation that can be replaced later.
- Alternatives considered: Centralized logging (ELK, Loki) – overkill for experimental phase.

### Safety & Input Sanitization
- Decision: Reject unsafe content per Microsoft content policy; filter prompts for disallowed content; avoid chain-of-thought exposure; strip excessive input length to defined max.
- Rationale: Aligns policy and constitution; reduces risk of harmful outputs.
- Alternatives considered: Post-hoc moderation only (riskier), allow all content (violates policy).

### Tools Interface (Agent Calls)
- Decision: Define DSPy `Tool` wrappers around existing services: `nl_search(query)` using `src/services/nl_search_service.py` and `validate_resource(url)` using `src/utils/link_verifier.py`. Orchestrate via a DSPy `Module` implementing ReACT.
- Rationale: Reuse existing code; leverage DSPy tool semantics and planning; minimal new surface.
- Alternatives considered: Custom orchestration without DSPy (loses DSPy benefits), building new services (duplicate work).

## Derived Policies from Spec
- Citations included only on explicit request.
- Tool traces never exposed; internal-only logs.
- Endpoint labeled experimental; avoid definitive claims when evidence insufficient.
- Rate limit: 5 requests/min per user.

## Implementation Notes
- Provide graceful fallback if Ollama/DSPy backend unavailable (return limitation message without error).
- Ensure consistent JSON response format across success and error cases.
- Add tests in contract, integration, and unit layers per constitution.
- Do not expose chain-of-thought; only final answers. Citations on explicit request and validated via tool.

<!--
  Sync Impact Report (v2.0.0 - Simplified Principles)
  ==================================================
  Version Change: 1.0.0 → 2.0.0 (MAJOR - Removed principle)
  Date: 2025-12-26
  
  Changes:
  - REMOVED: Principle IV (Performance Requirements) - entire section removed
  - MODIFIED: Principle II (Testing Standards) - removed specific 80% coverage threshold
  - Principles now focus on code quality, testing structure, and UX consistency only
  
  Remaining Principles:
  - I. Code Quality: Type safety, clean code, linting standards
  - II. Testing Standards: Comprehensive test structure (coverage threshold removed)
  - III. UX Consistency: Error handling, API consistency, actionable feedback
  
  Templates Status:
  ✅ Templates remain compatible - no structural changes required
  ✅ CLAUDE.md updated to remove coverage/performance references
  
  Rationale for MAJOR bump:
  - Removing an entire principle (Performance Requirements) is backward-incompatible
  - Projects relying on performance SLAs must now define their own standards
  
  Follow-up TODOs:
  - None
-->

# Smart Fetcher Constitution

## Core Principles

### I. Code Quality

**Code MUST be maintainable, readable, and type-safe.** All Python code requires comprehensive type annotations using Pydantic models or standard type hints. Functions MUST be under 50 lines; longer implementations require decomposition with clear single-responsibility functions. Code MUST pass ruff linting with zero errors and follow ruff formatting standards (100 char line length, double quotes). Every public module, class, and function MUST have docstrings describing purpose, parameters, return values, and raised exceptions. No `# type: ignore` or similar suppressions without documented justification in adjacent comments.

**Rationale**: Type safety prevents runtime errors and improves IDE tooling. Short functions reduce cognitive load and improve testability. Consistent linting/formatting eliminates style debates and reduces PR friction. Documentation ensures knowledge transfer and reduces onboarding time.

---

### II. Testing Standards (NON-NEGOTIABLE)

**All code MUST have comprehensive test coverage.** Tests MUST be organized into three directories: `tests/unit/` (isolated logic, mocked dependencies), `tests/integration/` (multi-component interactions, real services), and `tests/contract/` (API endpoint schemas, response formats). External services (LLMs, databases, APIs) MUST be mocked in unit tests to ensure deterministic, fast execution. Integration tests MAY use real services but MUST provide clear setup instructions. Test names MUST follow pattern `test_<behavior>_<condition>` (e.g., `test_search_returns_empty_when_no_matches`). Tests MUST be executable via `pytest` with coverage reporting available.

**Rationale**: Comprehensive testing catches regressions early and documents behavior. Structured test directories make test intent clear (unit=fast/isolated, integration=realistic scenarios, contract=API guarantees). Mocking external dependencies prevents flaky tests and enables CI without external service access. Clear naming makes failures instantly understandable.

---

### III. UX Consistency

**All API responses MUST follow consistent JSON structures.** Success responses MUST wrap data in descriptive objects (e.g., `{"results": [...], "count": N, "query": "..."}`) rather than bare arrays. Error responses MUST include `{"error": "<human-readable message>", "code": "<MACHINE_CODE>", "query": "<original-input>"}`. HTTP status codes MUST match semantics (200 success, 404 not found, 400 client error, 500 server error). Error messages MUST be actionable (e.g., "Tag parameter required" not "Invalid request"). CLI tools MUST write JSON output to stdout and errors to stderr. Exit codes MUST be 0 for success, non-zero for errors.

**Rationale**: Consistent response structures reduce client integration burden and prevent parsing errors. Wrapped formats enable metadata addition without breaking changes. Machine-readable error codes enable automated error handling. Actionable messages reduce support requests and debugging time. Proper exit codes enable shell scripting and CI integration.

---

## Development Workflow & Quality Gates

**All code MUST pass quality gates before merge.** Required checks: (1) `pytest` with all tests passing, (2) `ruff check .` with zero errors, (3) `mypy src/` with zero type errors, (4) `ruff format --check .` with zero formatting violations. Coverage reporting is encouraged but no minimum threshold enforced. Quality gates MUST be automated in CI where available. PRs with gate failures MUST NOT be merged without explicit constitution exception documentation. Gate failures MAY be temporarily bypassed with TODO comments and tracking issues ONLY if blocking critical bugfixes; bypass PRs MUST include remediation plan with timeline.

**Pre-Phase Checklist**: Before beginning Phase 0 research, verify: (1) All principles addressed in plan.md Constitution Check table, (2) Testing strategy defined (unit/integration/contract structure), (3) Error handling approach documented (consistent JSON wrapping). Re-verify after Phase 1 design with updated requirements from research.

**Documentation Requirements**: Every feature specification MUST include measurable success criteria tied to these principles (e.g., "comprehensive test suite passing", "zero ruff errors", "consistent error handling"). Implementation plans MUST reference constitution principles in their "Constitution Check" section and document any violations requiring complexity justification.

---

## Governance

**This constitution supersedes all other development practices.** When conflicts arise between constitution requirements and external guidelines (coding standards, team conventions, legacy patterns), constitution principles take precedence unless explicitly documented as exceptions. All code reviews MUST verify constitutional compliance before approval. Reviewers MUST challenge code that violates principles; authors MUST provide documented justification for exceptions.

**Amendment Procedure**: Constitutional amendments require: (1) Explicit version bump following semantic versioning (MAJOR for backward-incompatible changes like removing principles or changing testing thresholds, MINOR for new principles or expanded guidance, PATCH for clarifications and typo fixes), (2) Documentation of rationale in Sync Impact Report comment, (3) Review of dependent templates (plan-template.md, spec-template.md, tasks-template.md) with consistency updates, (4) Update of `LAST_AMENDED_DATE` to current date in ISO 8601 format. `RATIFICATION_DATE` remains fixed at initial adoption.

**Compliance Review**: Constitution alignment MUST be verified at three checkpoints: (1) During planning (pre-Phase 0 gate check), (2) After design (post-Phase 1 validation), (3) Before feature merge (final quality gate verification). Projects MAY document persistent deviations in a `EXCEPTIONS.md` file at repository root with per-exception justification and remediation timeline.

**Version**: 2.0.0 | **Ratified**: 2025-12-26 | **Last Amended**: 2025-12-26

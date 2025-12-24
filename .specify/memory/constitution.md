<!--
  Sync Impact Report
  ==================
  Version change: N/A → 1.0.0 (initial creation)

  Added Principles:
  - I. Code Quality
  - II. Testing Standards
  - III. User Experience Consistency
  - IV. Performance Requirements

  Added Sections:
  - Core Principles (4 principles)
  - Development Workflow
  - Quality Gates
  - Governance

  Removed Sections: None (initial creation)

  Templates Status:
  - .specify/templates/plan-template.md: ✅ Compatible (Constitution Check section present)
  - .specify/templates/spec-template.md: ✅ Compatible (requirements and success criteria align)
  - .specify/templates/tasks-template.md: ✅ Compatible (testing phases and quality tasks align)
  - .specify/templates/commands/*.md: ✅ No command files present

  Follow-up TODOs: None
-->

# Smart-Fetcher Constitution

## Core Principles

### I. Code Quality

All code MUST adhere to Python best practices and maintain high readability standards.

- **Type Annotations**: All functions and methods MUST include complete type hints for parameters and return values
- **Linting**: Code MUST pass `ruff` checks with zero warnings before merge
- **Formatting**: All code MUST be formatted with `ruff format` (or equivalent standard formatter)
- **Documentation**: Public APIs MUST have docstrings explaining purpose, parameters, and return values
- **Naming**: Variables, functions, and classes MUST use descriptive, intention-revealing names
- **Complexity**: Functions MUST NOT exceed 50 lines; cyclomatic complexity MUST NOT exceed 10
- **DRY Principle**: Duplicated logic MUST be extracted when it appears 3+ times

**Rationale**: Consistent, readable code reduces onboarding time, minimizes bugs, and enables confident refactoring.

### II. Testing Standards

All features MUST have comprehensive test coverage before release.

- **Coverage Threshold**: New code MUST maintain minimum 80% line coverage
- **Test Structure**: Tests MUST be organized into `unit/`, `integration/`, and `contract/` directories
- **Test Naming**: Test functions MUST clearly describe the scenario being tested (e.g., `test_fetch_returns_cached_response_when_url_seen_before`)
- **Isolation**: Unit tests MUST NOT make network calls or access external resources
- **Mocking**: External dependencies MUST be mocked in unit tests; integration tests MAY use real dependencies
- **CI Gate**: All tests MUST pass before merging to main branch
- **Regression Tests**: Bug fixes MUST include a test that reproduces the original issue

**Rationale**: Automated testing provides confidence for refactoring, catches regressions early, and documents expected behavior.

### III. User Experience Consistency

All user-facing interfaces MUST provide predictable, intuitive behavior.

- **Error Messages**: User-visible errors MUST be actionable and explain how to resolve the issue
- **CLI Output**: Command-line output MUST follow a consistent format (JSON for machine consumption, human-readable for interactive use)
- **Exit Codes**: CLI commands MUST use standard exit codes (0 = success, 1 = general error, 2 = usage error)
- **Progress Feedback**: Long-running operations MUST provide progress indication
- **Configuration**: All configurable options MUST have sensible defaults
- **Documentation**: User-facing features MUST have corresponding usage documentation
- **Backward Compatibility**: Breaking changes to public APIs MUST be clearly communicated and versioned

**Rationale**: Consistent UX reduces user frustration, support burden, and enables users to build reliable workflows.

### IV. Performance Requirements

Code MUST meet defined performance standards appropriate to the use case.

- **Response Time**: HTTP fetch operations MUST complete within configurable timeout (default: 30 seconds)
- **Memory Efficiency**: Memory usage MUST NOT grow unbounded; caches MUST have size limits
- **Concurrency**: I/O-bound operations SHOULD use async/await patterns for efficiency
- **Profiling**: Performance-critical paths MUST be profiled before optimization
- **Benchmarks**: Performance-sensitive features SHOULD include reproducible benchmarks
- **Resource Cleanup**: All acquired resources (connections, files, handles) MUST be properly released
- **Degradation**: System MUST degrade gracefully under load rather than fail catastrophically

**Rationale**: Predictable performance characteristics enable reliable integration and prevent resource exhaustion.

## Development Workflow

All development work MUST follow this workflow:

1. **Branch Strategy**: Feature work MUST occur on feature branches named `<issue-number>-<brief-description>`
2. **Commit Messages**: Commits MUST follow conventional commit format (e.g., `feat:`, `fix:`, `docs:`, `refactor:`)
3. **Pull Requests**: All changes to main MUST go through pull request review
4. **Code Review**: PRs MUST be reviewed by at least one other contributor before merge
5. **CI Checks**: All CI checks MUST pass before merge (tests, linting, type checking)
6. **Documentation**: User-facing changes MUST update relevant documentation in the same PR

## Quality Gates

Before any release, the following gates MUST be satisfied:

| Gate | Requirement | Verification |
|------|-------------|--------------|
| Tests | All tests pass | `uv run pytest` exits 0 |
| Coverage | ≥80% line coverage | Coverage report shows threshold met |
| Linting | Zero lint errors | `uv run ruff check .` exits 0 |
| Type Check | Zero type errors | `uv run mypy src/` exits 0 |
| Format | Code properly formatted | `uv run ruff format --check .` exits 0 |
| Docs | README accurate | Manual review confirms accuracy |

## Governance

This constitution supersedes all other development practices for the smart-fetcher project.

**Amendment Process**:
1. Propose amendment via pull request to this file
2. Document rationale for the change
3. Obtain approval from project maintainers
4. Update version number according to semantic versioning rules

**Versioning Policy**:
- MAJOR: Backward-incompatible governance or principle changes
- MINOR: New principles, sections, or material expansions
- PATCH: Clarifications, wording improvements, typo fixes

**Compliance**:
- All PRs MUST verify compliance with constitution principles
- Constitution violations MUST be documented and justified if temporarily necessary
- Regular reviews SHOULD occur to ensure constitution remains relevant

**Version**: 1.0.0 | **Ratified**: 2025-12-24 | **Last Amended**: 2025-12-24

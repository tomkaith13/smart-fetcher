# Research: Smart Tag-Based Resource Fetcher

**Date**: 2025-12-24
**Branch**: `001-dspy-tag-fetcher`

## 1. DSPy + Ollama Integration

### Decision
Use `dspy.LM("ollama_chat/gpt-oss:20b", ...)` pattern for local Ollama integration.

### Rationale
- Direct integration via `ollama_chat/<model>` prefix is the recommended modern approach
- Supports async workers for concurrent requests
- No API key required for local Ollama instances

### Configuration Pattern

```python
import dspy

# Initialize Ollama backend
lm = dspy.LM(
    "ollama_chat/gpt-oss:20b",
    api_base="http://localhost:11434",
    api_key=""
)

# Configure globally
dspy.configure(lm=lm)
```

### Alternatives Considered
- `dspy.OllamaLocal(model="...")` - older API, still works but less flexible
- OpenAI API - requires external service and API key costs

### Sources
- [DSPy Language Models Documentation](https://dspy.ai/learn/programming/language_models/)
- [Ollama + DSPy GitHub Gist](https://gist.github.com/jrknox1977/78c17e492b5a75ee5bbaf9673aee4641)
- [Reference implementation](https://github.com/tomkaith13/safety-classifier/blob/main/main.py)

---

## 2. DSPy Signature Design for Semantic Tag Matching

### Decision
Use class-based DSPy Signature with search tag as input and matching resource UUIDs as output.

### Rationale
- Single input (search_tag) keeps the interface simple
- The module internally has access to all resources via context
- Returns UUIDs of matching resources for direct lookup
- Cleaner separation: LLM decides semantic matches, Python handles resource retrieval

### Signature Pattern

```python
import dspy
from src.models.resource import Resource

class SemanticResourceFinder(dspy.Signature):
    """Given a search tag, find all resources that are semantically related to that tag.
    Consider synonyms, related concepts, and contextual similarity."""

    search_tag: str = dspy.InputField(desc="The tag to search for (e.g., 'home', 'car', 'technology')")
    resources_context: str = dspy.InputField(desc="JSON list of all available resources with their tags")
    matching_uuids: list[str] = dspy.OutputField(desc="UUIDs of resources whose tags are semantically related to the search tag")


# Usage with ChainOfThought for better reasoning
class SemanticSearchService:
    def __init__(self, resources: list[Resource]):
        self.resources = resources
        self.finder = dspy.ChainOfThought(SemanticResourceFinder)
        # Pre-build context string once
        self.resources_context = json.dumps([
            {"uuid": r.uuid, "tag": r.search_tag} for r in resources
        ])

    def find_matching(self, search_tag: str) -> list[Resource]:
        result = self.finder(
            search_tag=search_tag,
            resources_context=self.resources_context
        )
        # Look up full resources by returned UUIDs
        uuid_set = set(result.matching_uuids)
        return [r for r in self.resources if r.uuid in uuid_set]
```

### Alternative Approach - Direct Resource Output

```python
# If the LLM should return full resource objects (higher token cost)
class SemanticResourceFinder(dspy.Signature):
    """Find resources semantically related to the search tag."""

    search_tag: str = dspy.InputField(desc="The tag to search for")
    resources_json: str = dspy.InputField(desc="All available resources as JSON")
    matched_resources: list[dict] = dspy.OutputField(desc="List of matching resource objects")
```

### Alternatives Considered
- Two-input signature (tag + candidates) - requires extra orchestration layer
- Embedding-based similarity - more complex, requires vector DB
- Return full objects from LLM - higher token cost, potential parsing issues

### Sources
- [DSPy Signatures Documentation](https://dspy.ai/learn/programming/signatures/)
- [DSPy Signatures GitHub](https://github.com/stanfordnlp/dspy/blob/main/docs/docs/learn/programming/signatures.md)

---

## 3. Deterministic Resource Generation

### Decision
Use Python's `random.seed()` combined with `Faker.seed()` for reproducible resource generation.

### Rationale
- Setting both seeds ensures complete reproducibility across restarts
- Faker provides realistic names, descriptions, and domain-appropriate data
- Same 100 resources generated every time with identical UUIDs, names, and tags

### Implementation Pattern

```python
import random
import uuid
from faker import Faker

SEED = 42

def generate_resources(count: int = 100) -> list[Resource]:
    # Set seeds for reproducibility
    random.seed(SEED)
    Faker.seed(SEED)
    fake = Faker()
    fake.seed_instance(SEED)

    resources = []
    for _ in range(count):
        # Use seeded random for UUID generation
        resource_uuid = str(uuid.UUID(int=random.getrandbits(128)))
        resources.append(Resource(
            uuid=resource_uuid,
            name=fake.catch_phrase(),
            description=fake.paragraph(nb_sentences=2),
            search_tag=random.choice(TAG_CATEGORIES)
        ))
    return resources
```

### Tag Categories for Testing

A diverse set of 15 categories to enable meaningful semantic search testing:

```python
TAG_CATEGORIES = [
    "home",        # -> house, residence, dwelling, apartment
    "car",         # -> automobile, vehicle, transport
    "technology",  # -> tech, digital, electronics, computing
    "food",        # -> cuisine, meal, dining, nutrition
    "health",      # -> wellness, medical, fitness, healthcare
    "finance",     # -> money, banking, investment, economy
    "travel",      # -> trip, journey, vacation, tourism
    "education",   # -> learning, school, academic, training
    "sports",      # -> athletics, fitness, recreation, games
    "music",       # -> audio, sound, entertainment, concert
    "fashion",     # -> clothing, apparel, style, wardrobe
    "nature",      # -> environment, outdoors, wildlife, ecology
    "work",        # -> job, career, employment, office
    "family",      # -> relatives, household, domestic, kinship
    "art",         # -> creative, design, visual, artistic
]
```

### Alternatives Considered
- `secrets` module - designed for cryptographic randomness, not reproducible
- Hardcoded fixture file - less flexible, harder to modify count
- Database seeding - overkill for in-memory demo

### Sources
- [DataCamp Faker Tutorial](https://www.datacamp.com/tutorial/creating-synthetic-data-with-python-faker-tutorial)
- [Machine Learning Mastery - Synthetic Dataset Generation](https://machinelearningmastery.com/synthetic-dataset-generation-with-faker/)

---

## 4. FastAPI Integration Pattern

### Decision
Use FastAPI with Pydantic models for request/response schemas, async endpoints for LLM calls.

### Rationale
- FastAPI natively supports async/await for non-blocking LLM inference
- Pydantic provides automatic validation and OpenAPI schema generation
- Built-in support for the wrapped JSON response format defined in spec

### Implementation Pattern

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class SearchResponse(BaseModel):
    results: list[Resource]
    count: int
    query: str

class ErrorResponse(BaseModel):
    error: str
    code: str
    query: str

@app.get("/search", response_model=SearchResponse)
async def search_by_tag(tag: str) -> SearchResponse:
    if not tag or not tag.strip():
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                error="Tag parameter is required",
                code="MISSING_TAG",
                query=tag or ""
            ).model_dump()
        )

    # SemanticSearchService.find_matching takes only the tag,
    # returns list of matching Resource objects
    matched = semantic_search_service.find_matching(tag)
    return SearchResponse(results=matched, count=len(matched), query=tag)
```

### Alternatives Considered
- Flask - less async support, manual schema handling
- Starlette directly - more boilerplate, less automatic validation

---

## Summary

All technical unknowns have been resolved:

| Area | Decision | Confidence |
|------|----------|------------|
| LLM Backend | Ollama via `dspy.LM("ollama_chat/gpt-oss:20b")` | High |
| Semantic Matching | `SemanticResourceFinder` signature: tag in → matching UUIDs out | High |
| Data Generation | Faker + random.seed(42) for reproducibility | High |
| API Framework | FastAPI with Pydantic response models | High |
| Tag Categories | 15 diverse categories for meaningful testing | High |

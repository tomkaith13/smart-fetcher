# Quickstart: Natural Language UUID Search

## Run the API

```bash
uvicorn src.main:app --reload --port 8000
```

## Health Check

```bash
curl -s http://localhost:8000/health | jq
```

## NL Search Example

```bash
curl -s "http://localhost:8000/nl/search?q=show%20me%20resources%20that%20help%20me%20improve%20my%20hiking%20habits" | jq
```

Expected shape:

```json
{
  "results": [
    { "uuid": "...", "title": "...", "summary": "...", "link": "/resources/{uuid}" }
  ],
  "count": 3,
  "query": "show me resources that help me improve my hiking habits"
}
```

## Existing Endpoints

- `GET /search?tag=home` — tag-based semantic search
- `GET /resources/{uuid}` — retrieve resource
- `GET /resources` — list all resources

## Testing

```bash
pytest -q
ruff check .
mypy src/
```

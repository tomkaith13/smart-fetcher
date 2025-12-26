# Data Model: Ollama Health

## Entities

- HealthStatus (enum)
  - healthy | degraded | unhealthy

- OllamaStatus (enum)
  - connected | model_not_running | disconnected

- HealthSnapshot
  - status: HealthStatus
  - ollama: OllamaStatus
  - ollama_message: string
  - model_name: string
  - resources_loaded: int

## Relationships

- HealthSnapshot references configured model via `model_name`

## Validation Rules

- status MUST be one of the enum values
- ollama MUST be one of the enum values
- model_name MUST be non-empty
- resources_loaded MUST be >= 0

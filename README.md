# OpenAI API Blueprint

An implementation of the OpenAI API interface for building compatible LLM API services.

## Features

- Drop-in compatible with existing OpenAI API clients for chat completion
- Supports Chat Completions API
- Streaming support (Server-Sent Events)
- OpenAI-compatible authentication

## Requirements

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) for dependency management

## Setup

### Environment Variables

Create a `.env` file in the root directory with:

```
# Environment (development, test, staging, production)
# Valid values: development, test, staging, production
# Default: development
ENVIRONMENT=development

# Authentication
# Comma-separated list of valid API keys (minimum 16 characters each)
# REQUIRED FOR PRODUCTION/STAGING - application will fail to start if missing or invalid.
# Auto-generated for 'development' (dev_ prefix) or 'test' (test_ prefix) if not provided.
API_AUTH_TOKENS=your-production-token-12345678901234567890,another-token-12345678901234567890

# Server Configuration
# REQUIRED FOR PRODUCTION/STAGING
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# CORS Settings (comma-separated domains, optional)
# CORS_ORIGINS=http://localhost:3000,https://example.com

# Rate Limiting
# REQUIRED FOR PRODUCTION/STAGING
RATE_LIMIT_PER_MINUTE=10
```

#### Production Configuration Requirements

In production-like environments (`ENVIRONMENT=production` or `ENVIRONMENT=staging`), the application has strict configuration requirements enforced by Pydantic validation:

1. The following environment variables are **required**, and the application will fail to start if any are missing or invalid (e.g., `PORT` not an integer):
    *   `API_AUTH_TOKENS`: Must contain at least one token, each with a minimum of 16 characters.
    *   `HOST`: Server host address.
    *   `PORT`: Server port (must be a valid integer).
    *   `LOG_LEVEL`: Logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL).
    *   `RATE_LIMIT_PER_MINUTE`: Request rate limit per minute (must be a valid integer).

2. Project metadata (`project_name` and `project_version`) **must be available from `pyproject.toml`**. 
    *   The application will fail to start in production/staging if `project_name` or `project_version` cannot be read from `pyproject.toml` or are empty.

#### Development and Test Mode Behavior

In `development` and `test` environments, the application is more permissive:

1.  Missing or invalid values for `HOST`, `PORT`, `LOG_LEVEL`, `RATE_LIMIT_PER_MINUTE` will cause Pydantic validation errors and halt startup, but the error messages will indicate they are non-critical for these environments.
2.  `API_AUTH_TOKENS`:
    *   If `API_AUTH_TOKENS` is not provided or empty:
        *   In `development` mode, a secure random token prefixed with `dev_` is automatically generated and used. A warning is logged.
        *   In `test` mode, a fixed token `test_key` is used. A warning is logged.
    *   If tokens are provided but are too short (less than 16 characters), a warning is logged, but the application will proceed with those tokens.

#### Project Metadata

The application automatically reads project name and version exclusively from the `pyproject.toml` file. 

#### API Key Security

- In development mode: If no tokens are provided via `API_AUTH_TOKENS`, a secure random token with the prefix `dev_` will be generated and a warning logged.
- In test mode: If no tokens are provided, a consistent token `test_key` with the prefix `test_` is used and a warning logged.
- In production/staging mode:
    - You MUST provide strong API tokens (minimum 16 characters each) via the `API_AUTH_TOKENS` environment variable.
    - The application will fail to start if tokens are missing or do not meet the length requirement.
    - All tokens should be randomly generated, unique, and kept confidential.

### Local Development

1. Create and activate a virtual environment:

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:

```bash
uv pip install -e ".[dev]"
```

3. Run the API server:

```bash
uvicorn openai_api_blueprint.main:app --reload
```

The API will be available at http://127.0.0.1:8000. Visit http://127.0.0.1:8000/docs for interactive documentation.

### Docker

To run with Docker:

```bash
# Use BuildKit for faster builds with caching
export DOCKER_BUILDKIT=1

# Build the image
docker build -t openai-api-blueprint .

# Run with proper health checks and as non-root user
docker run -p 8000:8000 --env-file .env openai-api-blueprint
```

With Docker Compose (recommended for development):

```bash
# Enable BuildKit
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Start the service with watch mode for live reloading
docker compose up
```

For modern Docker Compose development with watch mode:

```bash
docker compose watch
```

## Testing

Run tests with pytest:

```bash
pytest
```

For only service tests:

```bash
pytest tests/services
```

For only API tests:

```bash
pytest tests/api
```

## API Usage

### Example: Chat Completions

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-production-token-12345678901234567890" \
  -d '{
    "model": "blueprint-standard",
    "messages": [
      {
        "role": "user",
        "content": "Hello!"
      }
    ]
  }'
```

### Example: Chat Completions with Streaming

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-production-token-12345678901234567890" \
  -d '{
    "model": "blueprint-standard",
    "messages": [
      {
        "role": "user",
        "content": "Hello!"
      }
    ],
    "stream": true
  }'
```

## Extending the Blueprint

To use this with actual LLM backends, modify the service implementations in `src/openai_api_blueprint/services/`.

## License

[MIT License](LICENSE)

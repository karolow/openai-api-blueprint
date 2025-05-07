# OpenAI API Blueprint

An implementation of the OpenAI API interface for building compatible LLM API services.

## Features

- Drop-in compatible with existing OpenAI API clients
- Supports Chat Completions API
- Streaming support (Server-Sent Events)
- OpenAI-compatible authentication
- Configurable model selection
- Docker-ready
- Comprehensive test suite

## Requirements

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) for dependency management

## Setup

### Environment Variables

Create a `.env` file in the root directory with:

```
# Authentication
# Comma-separated list of valid API keys
API_AUTH_TOKENS=your-test-token-1,your-test-token-2

# Logging
LOG_LEVEL=INFO

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60 

# Optional - for connecting to actual LLM backends
# OPENAI_API_KEY=your-openai-key
# ANTHROPIC_API_KEY=your-anthropic-key
# GOOGLE_API_KEY=your-google-key
```

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
  -H "Authorization: Bearer your-test-token-1" \
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
  -H "Authorization: Bearer your-test-token-1" \
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

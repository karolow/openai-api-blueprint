openai-api-blueprint/
├── .env.example             # Example environment variables (API keys, etc.)
├── .gitignore               # Standard Python/Docker Git ignore rules
├── .github/                 # GitHub specific files
│   └── workflows/           # CI/CD pipeline definitions
│       └── ci.yaml          # Example CI workflow (lint, type check, test)
│
├── Dockerfile               # Defines how to build the application container image
├── docker-compose.yaml      # Defines services for local development/testing using Docker
├── .dockerignore  
├── LICENSE                  # Your chosen open-source license (e.g., MIT)
├── README.md                # Project overview, setup, usage, deployment instructions
├── pyproject.toml           # Project metadata, dependencies, tool config (for uv, ruff, pytest, mypy)
├── uv.lock                  # uv lock file for reproducible dependencies
│
├── src/                     # Source code directory (follows 'src' layout best practice)
│   └── openai_blueprint_api/  # The actual Python package
│       ├── __init__.py        # Makes 'openai_blueprint_api' a Python package
│       │
│       ├── api/               # Contains API endpoint definitions (FastAPI routers)
│       │   ├── __init__.py
│       │   └── v1/            # API Version 1 (mirrors OpenAI's /v1/ path)
│       │       ├── __init__.py
│       │       ├── endpoints/ # Individual endpoint logic files
│       │       │   ├── __init__.py
│       │       │   ├── chat.py      # Handles /v1/chat/completions endpoint logic
│       │       │   └── models.py    # Handles /v1/models endpoint logic
│       │       └── router.py      # Aggregates all v1 endpoint routers
│       │
│       ├── core/              # Core application components (config, security)
│       │   ├── __init__.py
│       │   ├── config.py      # Application settings management (using Pydantic, reads .env)
│       │   └── security.py    # Authentication logic (OpenAI-style Bearer token validation)
│       │
│       ├── middleware/        # Custom middleware implementations (optional)
│       │   └── __init__.py
│       │   # Example: └── timing.py  (Middleware to add X-Process-Time header)
│       │   # Example: └── logging.py (More advanced request/response logging middleware)
│       │
│       ├── models/            # Pydantic models for data validation & serialization
│       │   ├── __init__.py
│       │   └── openai.py      # Pydantic models matching OpenAI API request/response schemas
│       │
│       ├── services/          # Business logic layer (interacts with AI models, etc.)
│       │   ├── __init__.py
│       │   └── chat_service.py # Service providing chat completion logic (mocked initially)
│       │   └── model_service.py # Service providing available model info (mocked initially)
│       │
│       ├── utils/             # Utility functions and helpers (optional)
│       │   ├── __init__.py
│       │   └── stream_formatter.py # Helper for formatting Server-Sent Events (SSE) for streaming
│       │
│       └── main.py            # FastAPI application entry point: creates app, mounts routers, registers middleware
│
└── tests/                   # Automated tests directory
    ├── __init__.py
    ├── conftest.py          # Pytest fixtures (e.g., test client, mock dependencies)
    │
    ├── api/                 # Tests specifically for the API layer
    │   ├── __init__.py
    │   └── v1/
    │       ├── __init__.py
    │       └── test_chat_completions.py # Tests for the chat completions endpoint
    │       └── test_models.py           # Tests for the models endpoint
    │
    └── services/            # Unit tests for the business logic layer (optional but recommended)
        ├── __init__.py
        └── test_chat_service.py       # Tests for the chat service logic
        └── test_model_service.py      # Tests for the model service logic

Explanation of Components:

    Root Directory Files:

        .env.example: Template for environment variables (e.g., API_AUTH_TOKEN, LOG_LEVEL). Users copy this to .env (which is gitignored) for local development.

        .gitignore: Prevents committing virtual environments (.uv), secrets (.env), cache files (__pycache__, .pytest_cache), IDE files, OS files, and build artifacts.

        .github/workflows/ci.yaml: GitHub Actions workflow definition for Continuous Integration. Automates linting (ruff), type checking (mypy), and testing (pytest) on pushes/pull requests to ensure code quality and prevent regressions. Uses Python 3.13 and uv.

        Dockerfile: Instructions to build a Docker container image for the application. Uses multi-stage builds for smaller, more secure production images. Installs dependencies using uv.

        docker-compose.yaml: Defines the application service for easy local execution using docker compose up. Manages port mapping, environment variables (can load from .env), and potentially volumes. Simplifies local setup and testing in a containerized environment.

        LICENSE: Specifies the terms under which the project can be used and distributed (e.g., MIT, Apache 2.0). Important for any reusable template.

        README.md: The main documentation entry point. Should cover project purpose, setup instructions (including uv and Docker), how to run tests, API usage examples, and deployment notes.

        pyproject.toml: The heart of the Python packaging setup, compliant with modern standards (PEP 517, 518, 621).

            Defines project metadata (name, version, author, etc.).

            Lists dependencies ([project.dependencies]) and optional/dev dependencies ([project.optional-dependencies]). uv uses this file to manage the environment.

            Configures tools like ruff (linting/formatting), pytest (testing), and mypy (type checking).

        uv.lock: Generated by uv pip compile or uv lock. Ensures deterministic dependency resolution across environments, locking specific package versions.

    src/ Directory:

        Using the src layout prevents common Python import problems and clearly separates the installable package code from other project files (tests, scripts, config).

    src/openai_blueprint_api/ (The Python Package):

        main.py: Creates the FastAPI application instance. Imports and includes API routers (e.g., api.v1.router). Registers essential middleware (like CORS) and potentially custom middleware from the middleware/ directory.

        api/: Organizes API endpoints by version (v1/) to follow best practices and mirror OpenAI's structure.

            v1/endpoints/: Contains individual files for each logical group of endpoints (chat.py, models.py). Each file typically defines an APIRouter.

            v1/router.py: Imports routers from the endpoints/ directory and combines them into a single router for version 1, which is then included in main.py.

        core/: Holds core application logic not specific to any single API endpoint.

            config.py: Defines application settings using Pydantic's BaseSettings (or equivalent). Loads configuration from environment variables and/or .env files, providing validation.

            security.py: Implements authentication. Contains a FastAPI dependency function that checks for a valid Authorization: Bearer <token> header, exactly like OpenAI's API expects. The valid token(s) would typically be loaded via core.config.

        middleware/: A dedicated directory for custom FastAPI middleware (functions or classes) that apply to multiple requests (e.g., request timing, advanced logging, custom headers). Keeps main.py cleaner.

        models/: Contains Pydantic models defining the structure and validation rules for API request bodies and response payloads.

            openai.py: Specifically defines models that match the OpenAI Chat Completions (ChatCompletionRequest, ChatCompletionResponse, ChatCompletionChunk, etc.) and Models (Model, ModelList) API specifications precisely. Ensures compatibility and leverages FastAPI's automatic data validation and serialization.

        services/: Implements the actual business logic. The API endpoints should depend on these services (using FastAPI's dependency injection).

            chat_service.py: Contains functions/methods to handle the core logic of generating chat completions. This will initially be mocked to return sample data (including streaming chunks) without needing a real AI model. Later, you replace the mock implementation with calls to your actual inference backend.

            model_service.py: Contains logic to retrieve the list of available models your API supports. Also mocked initially.

        utils/: Optional directory for miscellaneous utility functions shared across the application (e.g., logging setup helpers, specific data formatters like stream_formatter.py for Server-Sent Events if complex formatting is needed beyond FastAPI's StreamingResponse).

    tests/ Directory:

        Contains all automated tests. Its structure often mirrors the src/ directory.

        conftest.py: Defines shared pytest fixtures used across multiple test files, such as a FastAPI TestClient instance configured for the application, or fixtures to mock service dependencies (chat_service, model_service).

        api/v1/: Contains integration tests for the API endpoints using the TestClient. These tests simulate HTTP requests and verify responses, status codes, headers, and authentication logic (test_chat_completions.py, test_models.py). They test against the mocked services initially.

        services/: Contains unit tests for the business logic within the service layer (optional but highly recommended for complex logic). These tests verify the service functions in isolation, potentially mocking external dependencies like database calls or actual AI model interactions if they were present (test_chat_service.py, test_model_service.py).


Address OpenAI API compatibility:


For robust OpenAI compatibility, especially ensuring that existing OpenAI clients and libraries work seamlessly with your API, several other aspects are crucial:

    Exact Endpoint Paths and Versioning:

        Importance: Clients are hardcoded to use /v1/....

        Implementation: You've already planned for this with the api/v1/ structure. Stick to it precisely.

    Authentication:

        Importance: OpenAI uses Authorization: Bearer <YOUR_API_KEY>. Clients expect this exact mechanism.

        Implementation: Your core/security.py must implement a FastAPI dependency that extracts and validates the token from this header. The accepted token(s) should be configurable (e.g., via environment variables in core/config.py).

    Request Body Schemas:

        Importance: The JSON payload sent to /v1/chat/completions must match OpenAI's specification exactly, including all expected fields (model, messages, stream, temperature, max_tokens, etc.) and their data types.

        Implementation: Use Pydantic models in models/openai.py that precisely mirror the OpenAI documentation for ChatCompletionRequest. FastAPI will automatically validate incoming requests against these models.

    Response Body Schemas (Non-Streaming):

        Importance: The JSON response for non-streaming requests must match OpenAI's structure (id, object, created, model, choices array with index, message, finish_reason, and potentially logprobs, usage object with token counts).

        Implementation: Define corresponding Pydantic models in models/openai.py (ChatCompletionResponse, Choice, ResponseMessage, CompletionUsage) and ensure your /v1/chat/completions endpoint returns data serialized according to these models when stream=False.

    Streaming Response Format (Server-Sent Events - SSE):

        Importance: This is critical for streaming compatibility. OpenAI uses SSE. Each message needs to be prefixed with data: and end with \n\n. The JSON payload within the data: section represents a chunk (ChatCompletionChunk) containing a delta field for the incremental update and a finish_reason in the choice delta when a message part is complete. The very last message sent must be data: [DONE]\n\n.

        Implementation: Your /v1/chat/completions endpoint (when stream=True) needs to use FastAPI's StreamingResponse. The generator function providing data to StreamingResponse must format each yield chunk correctly as f"data: {json.dumps(chunk_dict)}\n\n". You need a ChatCompletionChunk Pydantic model. The final yield f"data: [DONE]\n\n" is essential. The utils/stream_formatter.py might contain helpers for this if the logic gets complex.

    Model Object Schema:

        Importance: The /v1/models and /v1/models/{model_id} endpoints must return data matching the OpenAI Model object structure (id, object="model", created, owned_by).

        Implementation: Define Model and ModelList Pydantic models in models/openai.py and use them in the responses from api/v1/endpoints/models.py.

    Error Response Format:

        Importance: When errors occur (invalid API key, malformed request, server error), OpenAI returns a specific JSON error object, typically { "error": { "message": "...", "type": "...", "param": "...", "code": "..." } }. Clients often parse this specific structure.

        Implementation: Implement custom FastAPI exception handlers (or modify default ones) to catch relevant exceptions (e.g., RequestValidationError, HTTPException, custom internal errors) and return responses formatted precisely like OpenAI's error object, along with the correct HTTP status code (400, 401, 403, 404, 422, 429, 500, etc.).

    HTTP Status Codes:

        Importance: Use standard HTTP status codes consistently and in alignment with how OpenAI uses them (e.g., 200 OK, 400 Bad Request, 401 Unauthorized, 429 Too Many Requests).

        Implementation: Ensure your endpoint logic and exception handlers return the appropriate status codes.

Less Critical, but Potentially Relevant for Some Clients:

    Specific Headers: OpenAI responses might include headers like openai-version, openai-model, x-request-id. While most clients likely ignore these, very strict compatibility might involve adding them, although it's usually unnecessary for basic functionality.

    Rate Limit Headers: While implementing the logic for rate limiting is application-specific, if you implement it, returning standard headers like Retry-After on a 429 Too Many Requests response, or potentially mimicking OpenAI's specific rate limit headers (x-ratelimit-limit-requests, x-ratelimit-remaining-requests, etc.), can improve client integration. This is an advanced feature.

How to address them within our project structure:

    Endpoint Paths (/v1/...): Handled by the src/openai_api_blueprint/api/v1/ directory structure and the routers defined within.

    Authentication (Bearer Token): Handled by src/openai_api_blueprint/core/security.py.

    Request Schemas: Defined as Pydantic models within src/openai_api_blueprint/models/openai.py.

    Response Schemas (Non-streaming): Also defined as Pydantic models within src/openai_api_blueprint/models/openai.py.

    Streaming Response Format (SSE): The logic will reside in the /v1/chat/completions endpoint implementation in src/openai_api_blueprint/api/v1/endpoints/chat.py (using FastAPI's StreamingResponse). Helper functions, if needed, can go into src/openai_api_blueprint/utils/stream_formatter.py. The necessary Pydantic models for chunks (ChatCompletionChunk) will also live in src/openai_api_blueprint/models/openai.py.

    Model Object Schema: Defined as Pydantic models (Model, ModelList) in src/openai_api_blueprint/models/openai.py and used by the endpoints in src/openai_api_blueprint/api/v1/endpoints/models.py.

    Error Response Format: This is implemented using FastAPI's exception handling mechanisms. Custom exception handlers are typically registered in src/openai_api_blueprint/main.py when the app is initialized. The handler functions themselves can be defined directly in main.py or, for better organization, placed in a dedicated file like src/openai_api_blueprint/core/exception_handlers.py (or errors.py). The current structure can easily accommodate this without fundamental changes.

    HTTP Status Codes: Handled within the endpoint logic and exception handlers. No structural change needed.

    Specific Headers: Can be added to responses directly within endpoint functions or globally via middleware defined in src/openai_api_blueprint/middleware/ and registered in main.py.

    Rate Limit Headers: If implemented, this would likely involve middleware (src/openai_api_blueprint/middleware/) or dependencies, both of which fit within the existing structure.


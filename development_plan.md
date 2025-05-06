Goal: Incrementally build the openai-api-blueprint template, ensuring each part works before moving to the next.

Tools: uv, Python 3.13, FastAPI, Pydantic, Pytest, Ruff, Mypy, Docker, Docker Compose, Git, GitHub Actions.

Phase 0: Project Setup & Foundation (The Skeleton)

    Goal: Create the basic project structure, initialize the environment, and set up tooling configs.

    Steps:

        Create the root directory: mkdir openai-api-blueprint && cd openai-api-blueprint

        Create the main directories: mkdir -p src/openai_api_blueprint tests .github/workflows

        Create essential files (empty for now, or with basic content):

            touch .env.example .gitignore LICENSE README.md Dockerfile docker-compose.yaml

            touch pyproject.toml uv.lock (uv.lock will be generated)

            touch src/openai_api_blueprint/__init__.py src/openai_api_blueprint/main.py

            touch tests/__init__.py tests/conftest.py

            Create __init__.py files in all subdirectories under src/openai_api_blueprint (api, api/v1, api/v1/endpoints, core, middleware, models, services, utils) and tests (api, api/v1, services).

            touch .github/workflows/ci.yaml

        Populate pyproject.toml:

            Define [project] metadata (name="openai-api-blueprint", version, description, authors, license, python=">=3.13").

            Add core [project.dependencies]: fastapi, uvicorn[standard], pydantic, pydantic-settings, python-dotenv.

            Add dev [project.optional-dependencies]: pytest, httpx (for testing), ruff, mypy.

            Configure tools ([tool.ruff], [tool.pytest.ini_options], [tool.mypy]). Basic Ruff rules, pytest test paths, mypy enabled.

        Populate .gitignore: Add standard Python (.uv, __pycache__, *.pyc), OS, IDE ignores, and .env.

        Initialize Environment: uv venv (creates .venv)

        Activate Environment: source .venv/bin/activate (or .\.venv\Scripts\activate on Windows)

        Install Dependencies: uv pip install -e ".[dev]" (Installs project in editable mode + dev dependencies)

        Basic FastAPI App (src/openai_api_blueprint/main.py):

              
        from fastapi import FastAPI

        app = FastAPI(
            title="OpenAI API Blueprint",
            description="Template for creating OpenAI-compatible APIs.",
            version="0.1.0",
        )

        @app.get("/health", tags=["Management"])
        async def health_check():
            """Basic health check endpoint."""
            return {"status": "ok"}

        # Placeholder for future router includes and middleware

            

        IGNORE_WHEN_COPYING_START

        Use code with caution. Python
        IGNORE_WHEN_COPYING_END

    Verification:

        Run uvicorn openai_api_blueprint.main:app --reload --port 8000.

        Access http://127.0.0.1:8000/health in your browser/curl. Should return {"status": "ok"}.

        Access http://127.0.0.1:8000/docs. Should show basic Swagger UI.

        Run ruff check . and ruff format . --check. Should pass (or show auto-fixable issues).

        Run mypy src. Should pass.

Phase 1: Configuration & /v1/models Endpoint (First Real Endpoint)

    Goal: Implement configuration loading and the /v1/models endpoint with mocked data.

    Steps:

        Configuration (src/openai_api_blueprint/core/config.py):

            Use pydantic-settings to define Settings class loading from .env.

            Add API_AUTH_TOKENS: str = "" (comma-separated valid tokens) and potentially LOG_LEVEL: str = "INFO".

        Populate .env.example: Add API_AUTH_TOKENS="your-test-token,another-token". Copy to .env.

        OpenAI Models (src/openai_api_blueprint/models/openai.py):

            Define Pydantic models: Model, ModelList. Ensure fields match OpenAI spec (id, object="model", created, owned_by).

        Model Service (src/openai_api_blueprint/services/model_service.py):

            Create a (mocked) function list_models() that returns a ModelList object with sample model data (e.g., id="mock-model-1", created=int(time.time()), owned_by="system").

            Create a (mocked) function get_model(model_id: str) that returns a single Model or raises HTTPException(404) if not found in the mock list.

        Models Endpoint (src/openai_api_blueprint/api/v1/endpoints/models.py):

            Create an APIRouter.

            Implement GET / endpoint (list_models_endpoint) that depends on list_models service function and returns ModelList.

            Implement GET /{model_id} endpoint (get_model_endpoint) that depends on get_model service function and returns Model.

        V1 Router (src/openai_api_blueprint/api/v1/router.py):

            Import the models router.

            Create a main v1_router = APIRouter(prefix="/v1").

            Include the models router: v1_router.include_router(models.router, prefix="/models", tags=["Models"]).

        Update main.py:

            Import v1_router from api.v1.router.

            Include the router: app.include_router(v1_router).

    Verification:

        Restart uvicorn.

        Access http://127.0.0.1:8000/v1/models. Should return the mocked list of models in the correct format.

        Access http://127.0.0.1:8000/v1/models/mock-model-1 (or your mock ID). Should return the single model details.

        Access http://127.0.0.1:8000/v1/models/nonexistent-model. Should return a 404 error.

        Check /docs - new endpoints should appear.

Phase 2: Authentication (OpenAI Style)

    Goal: Secure endpoints using Authorization: Bearer <token>.

    Steps:

        Security Dependency (src/openai_api_blueprint/core/security.py):

            Define oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") (tokenUrl is dummy, not used).

            Create an async function get_current_token(token: str = Depends(oauth2_scheme)) that:

                Loads allowed tokens from Settings.

                Checks if the provided token is in the allowed list.

                If not valid, raises HTTPException(status_code=401, detail="Invalid authentication credentials", headers={"WWW-Authenticate": "Bearer"}).

                If valid, returns the token (or True, or user info if you extend it later).

        Apply Security:

            Import the dependency get_current_token in api/v1/endpoints/models.py.

            Add dependencies=[Depends(get_current_token)] to the router definition in models.py (or individually to each endpoint path operation).

    Verification:

        Restart uvicorn.

        Access http://127.0.0.1:8000/v1/models without an Authorization header (e.g., using curl). Should get a 401 Unauthorized.

        Access http://127.0.0.1:8000/v1/models with Authorization: Bearer invalid-token. Should get 401 Unauthorized.

        Access http://127.0.0.1:8000/v1/models with Authorization: Bearer your-test-token (from .env). Should get 200 OK and the model list.

        Check /docs - the "Authorize" button should now appear.

Phase 3: /v1/chat/completions Endpoint (Non-Streaming)

    Goal: Implement the core chat completions endpoint, returning a single mocked response.

    Steps:

        Chat Models (src/openai_api_blueprint/models/openai.py):

            Define Pydantic models matching OpenAI: ChatMessage (role, content), ChatCompletionRequest (model, messages, stream, etc.), ChatCompletionResponseChoice, ResponseMessage, CompletionUsage, ChatCompletionResponse. Pay close attention to field names and types. Make stream optional, default False.

        Chat Service (src/openai_api_blueprint/services/chat_service.py):

            Create a (mocked) async function create_chat_completion(request: ChatCompletionRequest):

                Ignores most request parameters for now.

                Constructs and returns a sample ChatCompletionResponse object (e.g., with one choice containing a simple message like "This is a mocked response."). Include dummy id, created, model (matching request or a default), usage stats.

        Chat Endpoint (src/openai_api_blueprint/api/v1/endpoints/chat.py):

            Create an APIRouter.

            Implement POST /completions endpoint:

                Takes ChatCompletionRequest as the body.

                Depends on get_current_token for auth.

                Depends on the create_chat_completion service function.

                Returns the ChatCompletionResponse from the service.

                Crucially: Initially, ignore the request.stream flag (handle streaming in the next phase).

        Update V1 Router (src/openai_api_blueprint/api/v1/router.py):

            Import and include the chat router: v1_router.include_router(chat.router, prefix="/chat", tags=["Chat"]).

    Verification:

        Restart uvicorn.

        Use curl or a tool like Postman/Insomnia to send a POST request to http://127.0.0.1:8000/v1/chat/completions:

            Include Authorization: Bearer your-test-token.

            Include Content-Type: application/json.

            Provide a valid JSON body matching ChatCompletionRequest (e.g., {"model": "mock-model-1", "messages": [{"role": "user", "content": "Hello"}]}).

        Should receive a 200 OK with the mocked ChatCompletionResponse JSON.

        Try sending invalid JSON or missing required fields – should get 422 Unprocessable Entity.

        Check /docs for the new endpoint.

Phase 4: /v1/chat/completions Endpoint (Streaming)

    Goal: Add Server-Sent Events (SSE) streaming support.

    Steps:

        Streaming Models (src/openai_api_blueprint/models/openai.py):

            Define Pydantic models for streaming chunks: ChatCompletionChunkDelta, ChatCompletionChunkChoice, ChatCompletionChunk. Match OpenAI spec carefully (e.g., delta often only contains content or role, finish_reason appears in the choice).

        Update Chat Service (src/openai_api_blueprint/services/chat_service.py):

            Create a new (mocked) async generator function create_chat_completion_stream(request: ChatCompletionRequest):

                Yields multiple ChatCompletionChunk objects.

                Simulate receiving chunks of a message (e.g., yield a chunk with delta={"role": "assistant"}, then multiple chunks with delta={"content": "..."}, then a final chunk with finish_reason="stop" in the choice).

                Must yield objects that can be JSON-serialized.

        Update Chat Endpoint (src/openai_api_blueprint/api/v1/endpoints/chat.py):

            Modify the POST /completions endpoint:

                Check the request.stream flag.

                If True:

                    Call the streaming service function (create_chat_completion_stream).

                    Define an inner async generator function that iterates through the service's yielded chunks.

                    Inside the loop, format each chunk as SSE: yield f"data: {json.dumps(chunk.model_dump(exclude_unset=True))}\n\n". (Use model_dump or .dict() depending on Pydantic version).

                    Crucially, after the loop, yield "data: [DONE]\n\n".

                    Return a StreamingResponse with the inner generator and media_type="text/event-stream".

                If False: Call the non-streaming service function as before.

        (Optional) SSE Formatter (src/openai_api_blueprint/utils/stream_formatter.py): If formatting logic becomes complex, extract it into a helper function here.

    Verification:

        Restart uvicorn.

        Use curl -N (or a client library supporting SSE) to send a POST request to http://127.0.0.1:8000/v1/chat/completions with stream=True in the JSON body and valid auth.

        Observe the output: should see multiple data: {...} lines followed by data: [DONE].

        Verify the JSON structure within data: matches ChatCompletionChunk.

        Make a request with stream=False – should still return the single JSON response.

Phase 5: Testing

    Goal: Implement API tests using pytest and httpx.

    Steps:

        Test Client Fixture (tests/conftest.py):

            Create a pytest fixture client() that yields an httpx.AsyncClient instance configured to talk to the FastAPI app (using fastapi.testclient.TestClient is also common, but httpx is good for async).

        Models Endpoint Tests (tests/api/v1/test_models.py):

            Write tests for GET /v1/models and GET /v1/models/{model_id}.

            Test success cases (200 OK) with valid auth.

            Test authentication failures (401 Unauthorized) without/with invalid tokens.

            Test not found errors (404) for specific models.

            Assert response structure and status codes.

        Chat Completions Tests (tests/api/v1/test_chat_completions.py):

            Write tests for POST /v1/chat/completions.

            Test non-streaming success (200 OK) with valid auth and body. Assert response structure.

            Test streaming success (200 OK) with valid auth and stream=True. Capture the streamed response and assert it contains data: ... chunks and ends with data: [DONE]\n\n. Parse the JSON in the chunks.

            Test authentication failures (401).

            Test validation errors (422) with invalid request bodies.

        (Optional) Service Unit Tests (tests/services/): Write unit tests for the service functions if they contained complex logic (less critical when purely mocked).

    Verification:

        Run pytest in the terminal (from the project root). All tests should pass.

Phase 6: Containerization & CI

    Goal: Set up Docker, Docker Compose, and a basic CI pipeline.

    Steps:

        Dockerfile (Dockerfile):

            Use a multi-stage build.

            Builder Stage: Use a Python 3.13 base image, install uv, copy pyproject.toml and uv.lock, install dependencies using uv pip sync --no-deps pyproject.toml (or similar uv command to install locked deps), copy src/.

            Runtime Stage: Use a slim Python 3.13 image, copy installed dependencies and source code from the builder stage, expose port 8000, set CMD ["uvicorn", "openai_api_blueprint.main:app", "--host", "0.0.0.0", "--port", "8000"].

        Docker Compose (docker-compose.yaml):

            Define a service api.

            Build using the Dockerfile in the current context.

            Map port 8000:8000.

            Use env_file: .env to load environment variables.

            Set up a volume for hot-reloading during development (optional but useful): ./src:/app/src. Adjust CMD in Dockerfile or command in compose for uvicorn --reload.

        CI Workflow (.github/workflows/ci.yaml):

            Trigger on push and pull_request to main/master.

            Set up Python 3.13.

            Install uv.

            Install dependencies: uv pip install -e ".[dev]".

            Run Linters/Formatters: ruff check . --diff, ruff format . --check.

            Run Type Checker: mypy src tests.

            Run Tests: pytest.

    Verification:

        Run docker build . -t openai-api-blueprint-img. Should build successfully.

        Run docker compose up. The API should start and be accessible at http://localhost:8000. Test endpoints.

        Make a small change, commit, and push to GitHub (on a branch, then open a PR). The GitHub Action should trigger and pass.

Phase 7: Error Handling & Refinements

    Goal: Implement OpenAI-compatible error responses and general cleanup.

    Steps:

        OpenAI Error Model (src/openai_api_blueprint/models/openai.py):

            Define ErrorDetail (message, type, param, code) and ErrorResponse (error: ErrorDetail) Pydantic models.

        Custom Exception Handlers (src/openai_api_blueprint/main.py or core/exception_handlers.py):

            Add exception handlers using @app.exception_handler(...) for:

                HTTPException: Convert its detail into the ErrorDetail format.

                RequestValidationError (from FastAPI/Pydantic): Extract validation error details and format them into ErrorDetail (e.g., type='invalid_request_error', message from errors).

                Potentially a generic Exception handler for 500 errors, returning a standard server error message in the OpenAI format.

        Refine Logging: Integrate standard Python logging, configured via core/config.py. Add basic request logging middleware (maybe in middleware/logging.py).

        Documentation (README.md): Flesh out setup, usage examples (curl), testing, environment variables, and deployment notes.

        License (LICENSE): Choose and add an appropriate open-source license (e.g., MIT).

    Verification:

        Restart/rebuild.

        Trigger different errors (invalid auth, bad request body, nonexistent URL).

        Verify the JSON response body matches the ErrorResponse format.

        Check logs for request/error details.

        Review the README for clarity and completeness.
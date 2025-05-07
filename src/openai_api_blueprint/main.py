# src/openai_api_blueprint/main.py

"""
Main FastAPI application initialization and configuration.
"""

import logging

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer

from openai_api_blueprint.api.v1.router import v1_router
from openai_api_blueprint.core.config import settings
from openai_api_blueprint.core.errors import register_exception_handlers

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


def create_application() -> FastAPI:
    """
    Creates and configures the FastAPI application instance.

    Returns:
        FastAPI: The configured FastAPI application.
    """
    logger.info("Creating FastAPI application...")
    app_instance = FastAPI(
        title=settings.project_name,
        description="OpenAI-compatible API Blueprint",
        version=settings.project_version,
        docs_url="/docs" if settings.environment == "development" else None,
        redoc_url="/redoc" if settings.environment == "development" else None,
        openapi_url="/openapi.json" if settings.environment == "development" else None,
    )

    logger.info("Adding middleware...")
    app_instance.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.cors_origins]
        if settings.cors_origins
        else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register exception handlers for OpenAI-compatible error responses
    register_exception_handlers(app_instance)

    logger.info("Including API routers...")
    # Include the v1 API router
    app_instance.include_router(v1_router)

    # Health check endpoint for monitoring
    app_instance.get("/health", tags=["Management"], status_code=status.HTTP_200_OK)(health_check)

    logger.info("Application creation complete.")
    return app_instance


# Define the health check function before using it as a route handler
async def health_check() -> dict[str, str]:
    """
    Basic health check endpoint.

    Returns:
        dict: Status of the application.
    """
    logger.debug("Health check endpoint called")
    return {"status": "ok"}


app = create_application()

# Define the security scheme for Swagger UI
security_scheme = HTTPBearer(
    scheme_name="Bearer Authentication",
    description="Enter your API key with the 'Bearer ' prefix, e.g. 'Bearer test-token'",
)


if __name__ == "__main__":
    import uvicorn

    run_host = settings.host
    run_port = settings.port
    use_reload = settings.environment == "development"

    print(f"Starting Uvicorn server on {run_host}:{run_port} (Reload: {use_reload})...")
    uvicorn.run(
        "openai_api_blueprint.main:app",
        host=run_host,
        port=run_port,
        reload=use_reload,
        log_level=settings.log_level.lower(),
    )

# src/openai_api_blueprint/api/v1/router.py
"""
API Version 1 router.

This module aggregates all endpoints into a single v1 router
with the /v1 prefix for OpenAI API compatibility.
"""

from fastapi import APIRouter

from openai_api_blueprint.api.v1.endpoints import chat, models

# Main v1 router with /v1 prefix
v1_router = APIRouter(prefix="/v1")

# Include standard endpoint routers
v1_router.include_router(models.router, prefix="/models", tags=["Models"])
v1_router.include_router(chat.router, prefix="/chat/completions", tags=["Chat"])


@v1_router.get("/", tags=["Version 1"])
async def read_v1_root() -> dict[str, str]:
    """
    Root endpoint for v1 API.

    Returns:
        dict: A simple welcome message.
    """
    return {"message": "Welcome to OpenAI API Blueprint - Version 1"}

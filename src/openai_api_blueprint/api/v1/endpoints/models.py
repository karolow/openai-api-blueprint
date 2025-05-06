"""
Models endpoint for OpenAI API compatibility.

This module provides routes for listing available models and retrieving
specific model details.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status

from openai_api_blueprint.core.config import settings
from openai_api_blueprint.models.openai import Model, ModelList
from openai_api_blueprint.services import model_service

logger = logging.getLogger(__name__)

# Create router without prefix - prefix will be added in the main router
router = APIRouter()


def get_api_key(authorization: str = Header(None)) -> str:
    """
    Extract and validate the API key from the Authorization header.

    Args:
        authorization: The Authorization header value

    Returns:
        str: The validated API key

    Raises:
        HTTPException: If the API key is missing or invalid
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "message": "Missing API key",
                    "type": "authentication_error",
                    "code": "missing_api_key",
                }
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check for Bearer format
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "message": "Invalid authentication format. Use 'Bearer YOUR_TOKEN'",
                    "type": "authentication_error",
                    "code": "invalid_format",
                }
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = parts[1]
    if not settings.api_auth_tokens or token not in settings.api_auth_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "message": "Invalid API key",
                    "type": "authentication_error",
                    "code": "invalid_key",
                }
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token


@router.get(
    "",
    response_model=ModelList,
    summary="List models",
    description="Lists the currently available models, and provides basic information about each one such as the owner and availability.",
)
async def list_models_endpoint(api_key: Annotated[str, Depends(get_api_key)]) -> ModelList:
    """
    List available models.

    Args:
        api_key: The validated API key.

    Returns:
        ModelList: A list of available models.
    """
    logger.info("Listing all models")
    return model_service.list_models()


@router.get(
    "/{model_id}",
    response_model=Model,
    summary="Retrieve model",
    description="Retrieves a model instance, providing basic information about it such as the owner and availability.",
)
async def get_model_endpoint(model_id: str, api_key: Annotated[str, Depends(get_api_key)]) -> Model:
    """
    Get a specific model by ID.

    Args:
        model_id: The ID of the model to retrieve.
        api_key: The validated API key.

    Returns:
        Model: The requested model.

    Raises:
        HTTPException: If the model is not found.
    """
    logger.info(f"Getting model: {model_id}")
    return model_service.get_model(model_id)

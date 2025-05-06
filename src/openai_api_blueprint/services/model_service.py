"""
Model service for handling model-related operations.

This service provides functions for listing available models and retrieving
specific model details.
"""

import logging
import time

from fastapi import HTTPException, status

from openai_api_blueprint.models.openai import Model, ModelList

logger = logging.getLogger(__name__)

# Mock available models
# In a real implementation, these would likely come from a database or external service
AVAILABLE_MODELS = [
    Model(
        id="blueprint-standard",
        created=int(time.time()) - 10000,
        owned_by="openai-api-blueprint",
    ),
    Model(
        id="blueprint-advanced",
        created=int(time.time()) - 20000,
        owned_by="openai-api-blueprint",
    ),
    Model(
        id="blueprint-experimental",
        created=int(time.time()) - 5000,
        owned_by="openai-api-blueprint",
    ),
]


def list_models() -> ModelList:
    """
    List all available models.

    Returns:
        ModelList: A list of available models.
    """
    logger.debug(f"Listing {len(AVAILABLE_MODELS)} available models")
    return ModelList(data=AVAILABLE_MODELS)


def get_model(model_id: str) -> Model:
    """
    Get a specific model by ID.

    Args:
        model_id: The ID of the model to retrieve.

    Returns:
        Model: The requested model.

    Raises:
        HTTPException: If the model is not found.
    """
    logger.debug(f"Looking for model with ID: {model_id}")
    for model in AVAILABLE_MODELS:
        if model.id == model_id:
            return model

    logger.warning(f"Model not found: {model_id}")
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error": {
                "message": f"Model '{model_id}' not found",
                "type": "invalid_request_error",
                "param": "model_id",
                "code": "model_not_found",
            }
        },
    )

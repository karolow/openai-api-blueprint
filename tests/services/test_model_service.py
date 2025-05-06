"""
Tests for the model service module.
"""

from typing import TypedDict, cast

import pytest
from fastapi import HTTPException

from openai_api_blueprint.models.openai import Model, ModelList
from openai_api_blueprint.services import model_service


# Define TypedDict structures for error responses
class ErrorDetailDict(TypedDict):
    message: str
    type: str
    code: str
    param: str | None


class ErrorResponseDict(TypedDict):
    error: ErrorDetailDict


def get_error_detail(exception: HTTPException) -> ErrorResponseDict:
    """
    Helper function to safely extract and type error details from HTTPException.

    Args:
        exception: The HTTPException containing error details

    Returns:
        A properly typed dictionary with error information
    """
    # Cast the detail to our expected type
    return cast(ErrorResponseDict, exception.detail)


def test_list_models():
    """Test that list_models returns a ModelList with models."""
    result = model_service.list_models()

    # Check return type
    assert isinstance(result, ModelList)

    # Check that it contains models
    assert isinstance(result.data, list)
    assert len(result.data) > 0

    # Check the structure of the first model
    assert isinstance(result.data[0], Model)
    assert result.data[0].id is not None
    assert result.data[0].object == "model"
    assert result.data[0].created is not None
    assert result.data[0].owned_by is not None


def test_get_model_success():
    """Test that get_model returns the correct model when it exists."""
    # Get a real model ID from the list
    models_list = model_service.list_models()
    model_id = models_list.data[0].id

    # Get the model
    result = model_service.get_model(model_id)

    # Check return type
    assert isinstance(result, Model)

    # Check that it's the model we requested
    assert result.id == model_id
    assert result.object == "model"
    assert result.created is not None
    assert result.owned_by is not None


def test_get_model_not_found():
    """Test that get_model raises HTTPException when model doesn't exist."""
    nonexistent_id = "nonexistent-model-id"

    # Check that it raises HTTPException with 404 status code
    with pytest.raises(HTTPException) as exc_info:
        model_service.get_model(nonexistent_id)

    # Verify exception details
    assert exc_info.value.status_code == 404

    # Use the helper function to access error details safely
    error_response = get_error_detail(exc_info.value)

    # Check error structure
    assert "error" in error_response
    error = error_response["error"]

    # Verify error details
    assert "message" in error
    assert nonexistent_id in error["message"]
    assert error["type"] == "invalid_request_error"
    assert error["code"] == "model_not_found"

"""
Tests for the /v1/models API endpoints.
"""

from fastapi import status
from fastapi.testclient import TestClient

from openai_api_blueprint.core.config import settings


def test_list_models_unauthorized(client: TestClient) -> None:
    """Test that the list_models endpoint returns 401 without authorization."""
    response = client.get("/v1/models")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    error_data = response.json()
    assert "detail" in error_data
    assert "error" in error_data["detail"]
    assert error_data["detail"]["error"]["type"] == "authentication_error"
    assert error_data["detail"]["error"]["code"] == "missing_api_key"


def test_list_models_invalid_token(client: TestClient) -> None:
    """Test that the list_models endpoint returns 401 with invalid token."""
    response = client.get("/v1/models", headers={"Authorization": "Bearer invalid-token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    error_data = response.json()
    assert "detail" in error_data
    assert "error" in error_data["detail"]
    assert error_data["detail"]["error"]["type"] == "authentication_error"
    assert error_data["detail"]["error"]["code"] == "invalid_key"


def test_list_models_success(client: TestClient) -> None:
    """Test that the list_models endpoint returns 200 with valid token."""
    # Use the first token from settings
    token = settings.api_auth_tokens[0] if settings.api_auth_tokens else "test-token"

    response = client.get("/v1/models", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "object" in data
    assert data["object"] == "list"
    assert "data" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) > 0

    # Check structure of the first model
    model = data["data"][0]
    assert "id" in model
    assert "object" in model
    assert model["object"] == "model"
    assert "created" in model
    assert "owned_by" in model


def test_get_model_not_found(client: TestClient) -> None:
    """Test that the get_model endpoint returns 404 for nonexistent model."""
    # Use the first token from settings
    token = settings.api_auth_tokens[0] if settings.api_auth_tokens else "test-token"

    response = client.get(
        "/v1/models/nonexistent-model", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

    error_data = response.json()
    assert "detail" in error_data
    assert "error" in error_data["detail"]
    assert error_data["detail"]["error"]["type"] == "invalid_request_error"
    assert error_data["detail"]["error"]["code"] == "model_not_found"


def test_get_model_success(client: TestClient) -> None:
    """Test that the get_model endpoint returns 200 for existing model."""
    # Use the first token from settings
    token = settings.api_auth_tokens[0] if settings.api_auth_tokens else "test-token"

    # First, get the list of models
    list_response = client.get("/v1/models", headers={"Authorization": f"Bearer {token}"})
    assert list_response.status_code == status.HTTP_200_OK

    # Get the ID of the first model
    model_id = list_response.json()["data"][0]["id"]

    # Now request that specific model
    model_response = client.get(
        f"/v1/models/{model_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert model_response.status_code == status.HTTP_200_OK

    model_data = model_response.json()
    assert "id" in model_data
    assert model_data["id"] == model_id
    assert "object" in model_data
    assert model_data["object"] == "model"
    assert "created" in model_data
    assert "owned_by" in model_data

from typing import Generator

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from openai_api_blueprint.core.config import settings

ENDPOINT = "/v1/chat/completions"


@pytest.fixture
def valid_token() -> str:
    return settings.api_auth_tokens[0] if settings.api_auth_tokens else "test-token"


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    from openai_api_blueprint.main import app

    yield TestClient(app)


def test_chat_completion_non_streaming(client: TestClient, valid_token: str) -> None:
    payload = {
        "model": "blueprint-standard",
        "messages": [{"role": "user", "content": "Hello!"}],
        "stream": False,
    }
    response = client.post(
        ENDPOINT, json=payload, headers={"Authorization": f"Bearer {valid_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["object"] == "chat.completion"
    assert data["choices"][0]["message"]["role"] == "assistant"
    assert "THIS IS THE MOCKED CHAT RESPONSE" in data["choices"][0]["message"]["content"]


def test_chat_completion_streaming(client: TestClient, valid_token: str) -> None:
    payload = {
        "model": "blueprint-standard",
        "messages": [{"role": "user", "content": "Stream please!"}],
        "stream": True,
    }
    with client.stream(
        "POST", ENDPOINT, json=payload, headers={"Authorization": f"Bearer {valid_token}"}
    ) as response:
        assert response.status_code == status.HTTP_200_OK
        chunks = list(response.iter_lines())

        # Verify we got the [DONE] marker
        assert any("data: [DONE]" in chunk for chunk in chunks)

        # Check for MOCKED CHAT RESPONSE in any of the chunks (as part of the JSON)
        assert any("MOCKED" in chunk for chunk in chunks)
        # Can also look for other parts we expect in the JSON
        assert any('"content": "' in chunk for chunk in chunks)
        assert any('"finish_reason": "stop"' in chunk for chunk in chunks)


def test_chat_completion_invalid_model(client: TestClient, valid_token: str) -> None:
    payload = {"model": "not-a-real-model", "messages": [{"role": "user", "content": "Hello!"}]}
    response = client.post(
        ENDPOINT, json=payload, headers={"Authorization": f"Bearer {valid_token}"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert data["detail"]["error"]["code"] == "model_not_found"


def test_chat_completion_missing_auth(client: TestClient) -> None:
    payload = {"model": "blueprint-standard", "messages": [{"role": "user", "content": "Hello!"}]}
    response = client.post(ENDPOINT, json=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert data["detail"]["error"]["code"] == "missing_api_key"


def test_chat_completion_invalid_auth(client: TestClient) -> None:
    payload = {"model": "blueprint-standard", "messages": [{"role": "user", "content": "Hello!"}]}
    response = client.post(ENDPOINT, json=payload, headers={"Authorization": "Bearer wrong-token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert data["detail"]["error"]["code"] == "invalid_key"


def test_chat_completion_integration(client: TestClient, valid_token: str) -> None:
    # Full cycle: send a message, get a response, check structure
    payload = {
        "model": "blueprint-standard",
        "messages": [{"role": "user", "content": "What is this?"}],
    }
    response = client.post(
        ENDPOINT, json=payload, headers={"Authorization": f"Bearer {valid_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["object"] == "chat.completion"
    assert data["choices"][0]["message"]["role"] == "assistant"
    assert "THIS IS THE MOCKED CHAT RESPONSE" in data["choices"][0]["message"]["content"]

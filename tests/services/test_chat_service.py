"""
Unit tests for the chat completion service.
"""

from typing import Any

import pytest

from openai_api_blueprint.models.openai import ChatCompletionRequest, ChatMessage
from openai_api_blueprint.services.chat_service import ChatService


@pytest.fixture
def chat_service() -> ChatService:
    """Create a fresh instance of the ChatService for each test."""
    return ChatService()


@pytest.fixture
def sample_request() -> ChatCompletionRequest:
    """Create a sample chat completion request."""
    return ChatCompletionRequest(
        model="test-model",
        messages=[
            ChatMessage(role="system", content="You are a helpful assistant."),
            ChatMessage(role="user", content="Hello, how are you?"),
        ],
    )


@pytest.mark.asyncio
async def test_generate_completion(
    chat_service: ChatService, sample_request: ChatCompletionRequest
) -> None:
    """Test the non-streaming chat completion generation."""
    response = await chat_service.generate_completion(sample_request)

    # Verify response structure
    assert response.model == sample_request.model
    assert len(response.choices) == 1
    assert response.choices[0].index == 0
    assert response.choices[0].message.role == "assistant"
    assert response.choices[0].message.content is not None
    assert "THIS IS THE MOCKED CHAT RESPONSE" in response.choices[0].message.content
    assert response.choices[0].finish_reason == "stop"

    # Verify usage information is calculated
    assert response.usage.prompt_tokens > 0
    assert response.usage.completion_tokens > 0
    assert (
        response.usage.total_tokens
        == response.usage.prompt_tokens + response.usage.completion_tokens
    )


@pytest.mark.asyncio
async def test_generate_streaming_response(
    chat_service: ChatService, sample_request: ChatCompletionRequest
) -> None:
    """Test the streaming chat completion generation."""
    # Set stream flag to True
    sample_request.stream = True

    # Collect all chunks
    chunks: list[dict[str, Any]] = []
    async for chunk in chat_service.generate_streaming_response(sample_request):
        chunks.append(chunk)

    # Verify we got multiple chunks
    assert len(chunks) > 2, "Should have received multiple chunks"

    # Check first chunk has assistant role
    first_chunk = chunks[0]
    delta = first_chunk["choices"][0]["delta"]
    assert delta.get("role") == "assistant"

    # Check all chunks use the specified model
    for chunk in chunks:
        assert chunk["model"] == sample_request.model
        assert chunk["object"] == "chat.completion.chunk"

    # Check final chunk has finish_reason
    final_chunk = chunks[-1]
    assert final_chunk["choices"][0]["finish_reason"] == "stop"
    assert "delta" in final_chunk["choices"][0]
    delta_value = final_chunk["choices"][0]["delta"]
    assert not delta_value, "Final delta should be empty"


@pytest.mark.asyncio
async def test_streaming_chunks_form_valid_message(
    chat_service: ChatService, sample_request: ChatCompletionRequest
) -> None:
    """Test that streaming chunks can be combined to form a valid message."""
    sample_request.stream = True

    # Collect content from all chunks
    content_parts: list[str] = []
    async for chunk in chat_service.generate_streaming_response(sample_request):
        delta = chunk["choices"][0]["delta"]
        if "content" in delta and delta.get("content"):
            content_part = delta.get("content")
            if content_part:  # Ensure not None
                content_parts.append(content_part)

    # Combine the content parts
    full_content = "".join(content_parts)

    # Verify the combined content contains expected text
    assert "THIS IS THE MOCKED CHAT RESPONSE" in full_content

    # Compare with non-streaming response
    non_streaming_response = await chat_service.generate_completion(sample_request)
    non_streaming_content = non_streaming_response.choices[0].message.content

    # Check key phrases rather than exact words
    # since streaming and non-streaming messages differ slightly
    if non_streaming_content:
        # Common key phrases that should be in both messages
        key_phrases = ["THIS IS", "MOCKED", "CHAT", "RESPONSE", "OPENAI", "API", "BLUEPRINT"]
        for phrase in key_phrases:
            assert phrase in full_content, f"Key phrase '{phrase}' not found in streaming content"
            assert phrase in non_streaming_content, (
                f"Key phrase '{phrase}' not found in non-streaming content"
            )


@pytest.mark.asyncio
async def test_usage_calculation_scales_with_message_length(chat_service: ChatService) -> None:
    """
    Test that token usage calculations properly scale with message length.
    This tests internal service logic not directly verified in API tests.
    """
    # Create requests with different message lengths
    short_request = ChatCompletionRequest(
        model="test-model",
        messages=[ChatMessage(role="user", content="Hello!")],
    )

    long_request = ChatCompletionRequest(
        model="test-model",
        messages=[ChatMessage(role="user", content="Hello! " * 50)],  # Much longer message
    )

    # Get completions for both
    short_response = await chat_service.generate_completion(short_request)
    long_response = await chat_service.generate_completion(long_request)

    # Verify usage calculations
    assert short_response.usage.prompt_tokens < long_response.usage.prompt_tokens
    assert short_response.usage.prompt_tokens > 0
    assert long_response.usage.prompt_tokens > 0

    # Completion tokens should be the same since the response is mocked
    assert short_response.usage.completion_tokens == long_response.usage.completion_tokens

    # Total tokens should reflect the prompt token difference
    assert short_response.usage.total_tokens < long_response.usage.total_tokens
    token_diff = long_response.usage.total_tokens - short_response.usage.total_tokens
    prompt_token_diff = long_response.usage.prompt_tokens - short_response.usage.prompt_tokens
    assert token_diff == prompt_token_diff

"""
Chat completions endpoint for OpenAI API compatibility.

This module provides routes for generating chat completions.
"""

import asyncio
import logging
import time
import uuid
from typing import Annotated, Any, AsyncGenerator, Dict, Union

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from openai_api_blueprint.api.v1.endpoints.models import get_api_key
from openai_api_blueprint.models.openai import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionResponseChoice,
    ChatCompletionResponseMessage,
    UsageInfo,
)
from openai_api_blueprint.utils.stream import StreamingResponse

logger = logging.getLogger(__name__)

# Create router without prefix - prefix will be added in the main router
router = APIRouter()


async def generate_streaming_response(
    request: ChatCompletionRequest,
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Generate a streaming response for chat completion.

    Args:
        request: The chat completion request.

    Yields:
        Dict with each chunk of the response in OpenAI's streaming format.
    """
    # Create a response ID that will be consistent across chunks
    response_id = f"chatcmpl-{uuid.uuid4().hex}"
    created = int(time.time())

    # In a real implementation, you would use an actual AI model here and
    # yield tokens as they're generated. For this mock, we'll simulate streaming
    # by yielding the response one word at a time
    response_content = "THIS IS THE MOCKED CHAT RESPONSE FROM OPENAI API BLUEPRINT. If you see this message, your chat endpoint is working correctly with streaming!"
    words = response_content.split()

    # Stream each word with a small delay between them
    for i, word in enumerate(words):
        # Create the chunk in OpenAI's streaming format
        chunk = {
            "id": response_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": request.model,
            "choices": [
                {
                    "index": 0,
                    "delta": {
                        "content": word + " " if i > 0 else word,
                    }
                    if i > 0
                    else {
                        "role": "assistant",
                        "content": word + " ",
                    },
                    "finish_reason": None,
                }
            ],
        }

        # Real implementation would have more complex token logic
        yield chunk

        # Simulate processing time
        await asyncio.sleep(0.1)

    # Final chunk with finish_reason
    yield {
        "id": response_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": request.model,
        "choices": [
            {
                "index": 0,
                "delta": {},
                "finish_reason": "stop",
            }
        ],
    }


@router.post(
    "",
    response_model=ChatCompletionResponse,
    status_code=status.HTTP_200_OK,
    summary="Create a chat completion",
    description="Creates a completion for the chat message",
)
async def create_chat_completion(
    request: ChatCompletionRequest, api_key: Annotated[str, Depends(get_api_key)]
) -> Union[JSONResponse, StreamingResponse]:
    """
    Create a chat completion.

    Args:
        request: The chat completion request.
        api_key: The validated API key.

    Returns:
        ChatCompletionResponse or a streaming response.
    """
    logger.info(f"=== CHAT COMPLETION REQUESTED with model: {request.model} ===")
    logger.info(f"Stream mode: {request.stream}")

    # Log the incoming messages for debugging
    logger.info(f"Received {len(request.messages)} messages in the chat request")
    for idx, msg in enumerate(request.messages):
        logger.info(f"Message {idx} - Role: {msg.role}, Content: {msg.content}")

    # Check if streaming is requested
    if request.stream:
        logger.info("Returning streaming response")
        generator = generate_streaming_response(request)
        return await StreamingResponse.create_from_generator(generator)

    # For non-streaming responses, create a standard response
    response_content = "THIS IS THE MOCKED CHAT RESPONSE FROM OPENAI API BLUEPRINT. If you see this message, your chat endpoint is working correctly!"

    # Create the response
    response = ChatCompletionResponse(
        model=request.model,
        choices=[
            ChatCompletionResponseChoice(
                index=0,
                message=ChatCompletionResponseMessage(
                    role="assistant",
                    content=response_content,
                ),
                finish_reason="stop",
            )
        ],
        usage=UsageInfo(
            prompt_tokens=len("".join([msg.content or "" for msg in request.messages])),
            completion_tokens=len(response_content),
            total_tokens=len("".join([msg.content or "" for msg in request.messages]))
            + len(response_content),
        ),
    )

    logger.info("Returning chat completion response")
    return JSONResponse(content=response.model_dump())

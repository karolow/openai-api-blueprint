"""
Service for handling chat completions (mocked for now).
"""

import asyncio
import time
import uuid
from typing import Any, AsyncGenerator

from openai_api_blueprint.models.openai import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionResponseChoice,
    ChatCompletionResponseMessage,
    UsageInfo,
)


class ChatService:
    async def generate_streaming_response(
        self, request: ChatCompletionRequest
    ) -> AsyncGenerator[dict[str, Any], None]:
        response_id = f"chatcmpl-{uuid.uuid4().hex}"
        created = int(time.time())
        response_content = (
            "THIS IS THE MOCKED CHAT RESPONSE FROM OPENAI API BLUEPRINT. "
            "If you see this message, your chat endpoint is working correctly with streaming!"
        )
        words = response_content.split()
        for i, word in enumerate(words):
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
            yield chunk
            await asyncio.sleep(0.1)
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

    async def generate_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        response_content = (
            "THIS IS THE MOCKED CHAT RESPONSE FROM OPENAI API BLUEPRINT. "
            "If you see this message, your chat endpoint is working correctly!"
        )
        return ChatCompletionResponse(
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


# Dependency-injectable singleton
chat_service = ChatService()

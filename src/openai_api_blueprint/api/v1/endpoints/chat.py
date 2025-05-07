import logging
from typing import Annotated, Union

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

from openai_api_blueprint.api.v1.endpoints.models import get_api_key, limiter
from openai_api_blueprint.core.config import Settings, settings
from openai_api_blueprint.core.deps import get_settings
from openai_api_blueprint.models.openai import (
    ChatCompletionRequest,
    ChatCompletionResponse,
)
from openai_api_blueprint.services import model_service
from openai_api_blueprint.services.chat_service import ChatService, chat_service
from openai_api_blueprint.utils.stream import StreamingResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "",
    response_model=ChatCompletionResponse,
    status_code=status.HTTP_200_OK,
    summary="Create a chat completion",
    description="Creates a completion for the chat message",
)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")  # type: ignore
async def create_chat_completion(
    request: Request,
    chat_request: ChatCompletionRequest,
    api_key: Annotated[str, Depends(get_api_key)],
    chat_service: ChatService = Depends(lambda: chat_service),
    settings: Settings = Depends(get_settings),
) -> Union[JSONResponse, StreamingResponse]:
    logger.info(f"=== CHAT COMPLETION REQUESTED with model: {chat_request.model} ===")
    logger.info(f"Stream mode: {chat_request.stream}")

    # Stricter input validation: only allow known model IDs
    valid_model_ids = {model.id for model in model_service.AVAILABLE_MODELS}
    if chat_request.model not in valid_model_ids:
        client_host = getattr(request.client, "host", "unknown") if request.client else "unknown"
        logger.warning(f"Invalid model requested: {chat_request.model} from IP: {client_host}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "message": f"Model '{chat_request.model}' is not available.",
                    "type": "invalid_request_error",
                    "param": "model",
                    "code": "model_not_found",
                }
            },
        )

    logger.info(f"Received {len(chat_request.messages)} messages in the chat request")
    for idx, msg in enumerate(chat_request.messages):
        logger.info(f"Message {idx} - Role: {msg.role}, Content: {msg.content}")

    if chat_request.stream:
        logger.info("Returning streaming response")
        generator = chat_service.generate_streaming_response(chat_request)
        return await StreamingResponse.create_from_generator(generator)

    # For real model inference, use run_in_executor to avoid blocking the event loop:
    # import asyncio
    # loop = asyncio.get_running_loop()
    # response = await loop.run_in_executor(None, chat_service.generate_completion, chat_request)
    # return JSONResponse(content=response.model_dump())

    response = await chat_service.generate_completion(chat_request)
    logger.info("Returning chat completion response")
    return JSONResponse(content=response.model_dump())

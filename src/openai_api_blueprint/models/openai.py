"""
Pydantic models for OpenAI API compatibility.

These models define the structure of requests and responses to match
the OpenAI API specification.
"""

from time import time
from typing import Any, Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class Model(BaseModel):
    """
    Model information, matching OpenAI's Model object.
    """

    id: str
    object: Literal["model"] = "model"
    created: int = Field(default_factory=lambda: int(time()))
    owned_by: str = "openai-api-blueprint"


class ModelList(BaseModel):
    """
    List of models, matching OpenAI's ModelList response.
    """

    object: Literal["list"] = "list"
    data: list[Model]


# --- ChatCompletions Models ---


class ChatMessage(BaseModel):
    """
    A single message in a chat conversation.
    """

    role: Literal["system", "user", "assistant", "tool", "function"]
    content: str | None = None
    name: Optional[str] = None
    function_call: Optional[dict[str, Any]] = None
    tool_calls: Optional[list[dict[str, Any]]] = None


class ChatCompletionRequest(BaseModel):
    """
    Request for a chat completion.
    """

    model: str
    messages: list[ChatMessage]
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0
    stop: Optional[list[str] | str] = None
    user: Optional[str] = None
    tools: Optional[list[dict[str, Any]]] = None
    tool_choice: Optional[str | dict[str, Any]] = None
    function_call: Optional[str | dict[str, str]] = None
    functions: Optional[list[dict[str, Any]]] = None
    response_format: Optional[dict[str, str]] = None


class ChatCompletionResponseMessage(BaseModel):
    """
    A message in a chat completion response.
    """

    role: Literal["assistant"]
    content: str | None
    function_call: Optional[dict[str, Any]] = None
    tool_calls: Optional[list[dict[str, Any]]] = None


class ChatCompletionResponseChoice(BaseModel):
    """
    A single choice in a chat completion response.
    """

    index: int
    message: ChatCompletionResponseMessage
    finish_reason: Literal["stop", "length", "content_filter", "tool_calls", "function_call"] = (
        "stop"
    )


class UsageInfo(BaseModel):
    """
    Token usage information.
    """

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    """
    Response for a chat completion.
    """

    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid4().hex}")
    object: Literal["chat.completion"] = "chat.completion"
    created: int = Field(default_factory=lambda: int(time()))
    model: str
    choices: list[ChatCompletionResponseChoice]
    usage: UsageInfo

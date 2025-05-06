"""
Streaming utilities for OpenAI-compatible API responses.
"""

import asyncio
import json
from collections.abc import MutableMapping
from typing import Any, AsyncGenerator, Callable, Generator, Mapping, Optional, Union

from fastapi import Response
from starlette.background import BackgroundTask


class StreamingResponse(Response):
    """
    Custom streaming response for OpenAI-compatible API.

    This class handles streaming chat completion responses in the
    format expected by OpenAI clients.
    """

    media_type = "text/event-stream"

    def __init__(
        self,
        content: Union[AsyncGenerator[str, None], Generator[str, None, None]],
        status_code: int = 200,
        headers: Optional[Mapping[str, str]] = None,
        media_type: Optional[str] = None,
        background: Optional[BackgroundTask] = None,
    ):
        """Initialize the streaming response with a content generator."""
        self.content_generator = content
        self.status_code = status_code
        self.background = background

        # Prepare headers for SSE
        raw_headers: list[tuple[bytes, bytes]] = []
        if headers:
            raw_headers.extend([(key.encode(), value.encode()) for key, value in headers.items()])
        raw_headers.extend(
            [
                (b"Content-Type", b"text/event-stream"),
                (b"Cache-Control", b"no-cache"),
                (b"Connection", b"keep-alive"),
                (b"Transfer-Encoding", b"chunked"),
            ]
        )
        self.raw_headers = raw_headers

        if media_type is not None:
            self.media_type = media_type

    @staticmethod
    def _serialize_chunk(data: Any) -> str:
        """Serialize a chunk of data to SSE format."""
        json_data = json.dumps(data, ensure_ascii=False)
        return f"data: {json_data}\n\n"

    @staticmethod
    def _serialize_done() -> str:
        """Serialize the final [DONE] marker."""
        return "data: [DONE]\n\n"

    async def stream_response(self, send: Callable[[dict[str, Any]], Any]) -> None:
        """Stream the response in chunks."""
        await send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": self.raw_headers,
            }
        )

        async for chunk in self._get_content_generator():
            await send(
                {
                    "type": "http.response.body",
                    "body": chunk.encode("utf-8"),
                    "more_body": True,
                }
            )

        # Send the final [DONE] marker
        await send(
            {
                "type": "http.response.body",
                "body": self._serialize_done().encode("utf-8"),
                "more_body": True,
            }
        )

        # End the response
        await send(
            {
                "type": "http.response.body",
                "body": b"",
                "more_body": False,
            }
        )

    async def _get_content_generator(self) -> AsyncGenerator[str, None]:
        """Convert the content generator to an async generator if needed."""
        if isinstance(self.content_generator, AsyncGenerator):
            async for chunk in self.content_generator:
                yield self._serialize_chunk(chunk)
        else:
            # Handle regular generator by running it in a thread pool
            for chunk in self.content_generator:
                yield self._serialize_chunk(chunk)
                # Small delay to prevent blocking
                await asyncio.sleep(0.001)

    async def __call__(
        self,
        scope: MutableMapping[str, Any],
        receive: Callable[[], Any],
        send: Callable[[dict[str, Any]], Any],
    ) -> None:
        """ASGI application implementation."""
        await self.stream_response(send)

        if self.background is not None:
            await self.background()

    @classmethod
    async def create_from_generator(
        cls, generator: Union[AsyncGenerator[Any, None], Generator[Any, None, None]]
    ) -> "StreamingResponse":
        """Create a streaming response from a generator."""
        return cls(content=generator)

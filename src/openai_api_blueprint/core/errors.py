"""
Error handling utilities for standardized API errors in OpenAI format.
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ErrorDetail(BaseModel):
    """Standardized error detail format matching OpenAI API."""

    message: str
    type: str
    param: str | None = None
    code: str | None = None


class ErrorResponse(BaseModel):
    """Standard OpenAI error response wrapper."""

    error: ErrorDetail


def register_exception_handlers(app: FastAPI) -> None:
    """
    Configure exception handlers for the application to return OpenAI-compatible error responses.

    Args:
        app: The FastAPI application instance.
    """

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(  # type: ignore
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle validation errors with OpenAI-compatible format."""
        errors = exc.errors()
        logger.error(f"Validation error for request {request.url.path}:")
        logger.error(f"Request body: {await request.body()}")
        logger.error(f"Validation errors: {errors}")

        # Extract error details for better error messages
        error_message = "Invalid request data. Please check the input."
        error_param = None

        if errors and len(errors) > 0:
            error_detail = errors[0]
            error_loc = error_detail.get("loc", [])
            error_msg = error_detail.get("msg", "")

            if error_loc and len(error_loc) > 0:
                error_param = ".".join(str(loc) for loc in error_loc if loc)

            error_message = f"{error_msg} at {error_param}" if error_param else error_msg

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(
                error=ErrorDetail(
                    message=error_message,
                    type="invalid_request_error",
                    param=error_param,
                    code="validation_error",
                )
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:  # type: ignore
        """Handle unexpected errors with OpenAI-compatible format."""
        logger.exception(f"Unexpected error for {request.url.path}: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error=ErrorDetail(
                    message="An unexpected error occurred. Please try again later.",
                    type="server_error",
                    code="internal_server_error",
                )
            ).model_dump(),
        )

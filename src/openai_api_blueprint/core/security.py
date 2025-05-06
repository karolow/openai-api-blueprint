"""
Security utilities for API authentication.

This module provides functions for validating authentication tokens
in the OpenAI API format (Bearer token authentication).
"""

import logging
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from openai_api_blueprint.core.config import settings

logger = logging.getLogger(__name__)


async def get_api_key(authorization: str = Header(None)) -> str:
    """
    Extract and validate the API key from the Authorization header.

    Args:
        authorization: The HTTP Authorization header value.

    Returns:
        str: The validated API key.

    Raises:
        HTTPException: If no valid API key is provided or the key is invalid.
    """
    # No authorization header provided
    if not authorization:
        logger.warning("Missing authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "message": "Missing API key. Please provide a valid API key in the Authorization header using the Bearer scheme.",
                    "type": "authentication_error",
                    "code": "missing_api_key",
                }
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check for Bearer prefix
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        logger.warning("Invalid authorization header format")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "message": "Invalid authentication format. Please use 'Bearer YOUR_API_KEY'.",
                    "type": "authentication_error",
                    "code": "invalid_auth_format",
                }
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract the token
    token = parts[1]

    # Check API key against allowed tokens
    if not settings.api_auth_tokens or token not in settings.api_auth_tokens:
        logger.warning("Invalid API key provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "message": "Invalid API key. Please provide a valid API key in the Authorization header using the Bearer scheme.",
                    "type": "authentication_error",
                    "code": "invalid_api_key",
                }
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.debug("Valid API key provided")
    return token


# Create a dependency that can be injected into routes
validate_api_key = Annotated[str, Depends(get_api_key)]

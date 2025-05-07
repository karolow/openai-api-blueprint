"""
Application configuration settings.

Simple configuration for development phase.
"""

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load .env file if it exists
dotenv_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)


class Settings(BaseModel):
    """
    Application settings.
    """

    # Project metadata
    project_name: str = "OpenAI API Blueprint"
    project_version: str = "0.1.0"

    # Server settings
    host: str = Field(default=os.getenv("HOST", "0.0.0.0"))
    port: int = Field(default=int(os.getenv("PORT", "8000")))
    log_level: str = Field(default=os.getenv("LOG_LEVEL", "INFO"))
    environment: str = Field(default=os.getenv("ENVIRONMENT", "development"))

    # CORS settings
    cors_origins: list[str] = Field(default_factory=list)

    # Security settings
    api_auth_tokens: list[str] = Field(default_factory=list)

    # Rate limiting
    rate_limit_per_minute: int = Field(default=int(os.getenv("RATE_LIMIT_PER_MINUTE", "5")))

    def __init__(self, **data: Any):
        super().__init__(**data)

        # Process API tokens from environment
        tokens_str = os.getenv("API_AUTH_TOKENS", "")
        if tokens_str:
            self.api_auth_tokens = [
                token.strip() for token in tokens_str.split(",") if token.strip()
            ]

        # If no tokens are set, add defaults for development
        if not self.api_auth_tokens and self.environment == "development":
            self.api_auth_tokens = ["test-token", "dev-token"]

        # Process CORS origins from environment
        cors_str = os.getenv("CORS_ORIGINS", "")
        if cors_str:
            self.cors_origins = [origin.strip() for origin in cors_str.split(",") if origin.strip()]


# Create settings instance
settings = Settings()

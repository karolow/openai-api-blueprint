"""
Application configuration settings.

Configuration with strict validation in production environments.
"""

import logging
import os
import secrets
import sys
import tomllib
from enum import Enum
from pathlib import Path
from typing import Any, List, Self

from dotenv import find_dotenv, load_dotenv
from pydantic import BaseModel, Field, ValidationError, model_validator

load_dotenv(find_dotenv())

logger = logging.getLogger(__name__)

# Constants
MIN_TOKEN_LENGTH = 16
DEV_TOKEN_PREFIX = "dev_"
TEST_TOKEN_PREFIX = "test_"


class Environment(str, Enum):
    """Valid application environments."""

    DEVELOPMENT = "development"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


# Load project metadata from pyproject.toml
def load_project_metadata() -> dict[str, str]:
    """Load project name and version from pyproject.toml file."""
    try:
        # Define the expected path relative to this file's location
        # Assuming config.py is in src/openai_api_blueprint/core/
        # and pyproject.toml is at the project root.
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        toml_path = base_dir / "pyproject.toml"

        if toml_path.exists():
            with open(toml_path, "rb") as f:
                pyproject = tomllib.load(f)
                project_section = pyproject.get("project", {})
                name = project_section.get("name", "")
                version = project_section.get("version", "")

                if not name:
                    logger.warning("Project name not found in pyproject.toml [project.name].")
                if not version:
                    logger.warning("Project version not found in pyproject.toml [project.version].")

                return {"name": name, "version": version}

        logger.warning(f"Could not find or parse pyproject.toml at expected location: {toml_path}")
        return {"name": "", "version": ""}
    except Exception as e:
        logger.error(f"Error reading project metadata from pyproject.toml: {e}")
        return {"name": "", "version": ""}


# Load project metadata once at module level
project_metadata_loaded = load_project_metadata()


class Settings(BaseModel):
    """
    Application settings with validation.
    Pydantic handles type coercion and presence validation for required fields.
    Project name and version are sourced exclusively from pyproject.toml.
    """

    # Environment detection
    environment: Environment

    # Server settings (required, Pydantic will raise ValidationError if missing/invalid)
    host: str
    port: int
    log_level: str

    # Project metadata (sourced exclusively from pyproject.toml)
    project_name: str = Field(default_factory=lambda: project_metadata_loaded.get("name", ""))
    project_version: str = Field(default_factory=lambda: project_metadata_loaded.get("version", ""))

    # Security settings
    api_auth_tokens: List[str] = Field(default_factory=list)

    # CORS settings
    cors_origins: List[str] = Field(default_factory=list)

    # Rate limiting (required, Pydantic will raise ValidationError if missing/invalid)
    rate_limit_per_minute: int

    @model_validator(mode="after")
    def _validate_settings_post_init(self) -> Self:
        is_prod_or_staging = self.environment in (Environment.PRODUCTION, Environment.STAGING)

        # Validate API Tokens
        validated_tokens: list[str] = []
        current_tokens = list(self.api_auth_tokens)

        if not current_tokens:
            if is_prod_or_staging:
                raise ValueError(
                    f"No API authentication tokens configured in {self.environment.value} environment."
                )
            elif self.environment == Environment.DEVELOPMENT:
                dev_token = f"{DEV_TOKEN_PREFIX}{secrets.token_urlsafe(16)}"
                current_tokens = [dev_token]
                logger.warning(
                    f"DEVELOPMENT: No API tokens configured. Using auto-generated development token: {dev_token}. "
                    "This would not be allowed in production."
                )
            elif self.environment == Environment.TEST:
                test_token = f"{TEST_TOKEN_PREFIX}key"
                current_tokens = [test_token]
                logger.warning(
                    "TESTING: Using fixed test token for testing environment. "
                    "This would not be allowed in production."
                )

        for token in current_tokens:
            if len(token) < MIN_TOKEN_LENGTH:
                msg = f"API token is too short (less than {MIN_TOKEN_LENGTH} characters): '{token[:10]}...'"
                if is_prod_or_staging:
                    raise ValueError(f"{msg}. This is a security risk in production.")
                else:
                    logger.warning(f"{msg}. This would be rejected in production.")
            validated_tokens.append(token)

        self.api_auth_tokens = validated_tokens

        # Validate project metadata (sourced from pyproject.toml) in production/staging
        if is_prod_or_staging:
            if not self.project_name:
                raise ValueError(
                    "PROJECT_NAME must be available from pyproject.toml in production/staging environments."
                )
            if not self.project_version:
                raise ValueError(
                    "PROJECT_VERSION must be available from pyproject.toml in production/staging environments."
                )
        return self


# --- Main loading block ---
try:
    env_value_raw = os.getenv("ENVIRONMENT", Environment.DEVELOPMENT.value)
    try:
        environment_parsed = Environment(env_value_raw.strip().lower())
    except ValueError:
        logger.warning(
            f"Invalid ENVIRONMENT value: '{env_value_raw}'. Defaulting to '{Environment.DEVELOPMENT.value}'."
        )
        environment_parsed = Environment.DEVELOPMENT

    # Collect settings from environment variables.
    # project_name and project_version are no longer sourced from env.
    raw_settings_from_env: dict[str, Any] = {
        "environment": environment_parsed,
        "host": os.getenv("HOST"),
        "port": os.getenv("PORT"),
        "log_level": os.getenv("LOG_LEVEL"),
        "api_auth_tokens": [
            token.strip() for token in os.getenv("API_AUTH_TOKENS", "").split(",") if token.strip()
        ],
        "cors_origins": [
            origin.strip() for origin in os.getenv("CORS_ORIGINS", "").split(",") if origin.strip()
        ],
        "rate_limit_per_minute": os.getenv("RATE_LIMIT_PER_MINUTE"),
    }

    # project_name and project_version will be populated by Pydantic's default_factory
    # using project_metadata_loaded.
    settings = Settings(**raw_settings_from_env)

    logger.info(f"Settings loaded successfully for {settings.environment.value} environment.")

except ValidationError as e:
    env_for_error_handling_raw = (
        os.getenv("ENVIRONMENT", Environment.DEVELOPMENT.value).strip().lower()
    )
    is_prod_or_staging_for_error = env_for_error_handling_raw in (
        Environment.PRODUCTION.value,
        Environment.STAGING.value,
    )

    if is_prod_or_staging_for_error:
        logger.critical(
            f"FATAL: Settings validation failed in '{env_for_error_handling_raw}' environment. "
            f"Pydantic error: {e}"
        )
        sys.exit(1)
    else:
        logger.error(
            f"Settings validation error (non-critical in '{env_for_error_handling_raw}' environment): {e}"
        )
        raise
except ValueError as e:  # Catches errors from _validate_settings_post_init
    env_for_error_handling_raw = (
        os.getenv("ENVIRONMENT", Environment.DEVELOPMENT.value).strip().lower()
    )
    is_prod_or_staging_for_error = env_for_error_handling_raw in (
        Environment.PRODUCTION.value,
        Environment.STAGING.value,
    )
    if is_prod_or_staging_for_error:
        logger.critical(
            f"FATAL: Critical configuration error in '{env_for_error_handling_raw}' environment: {e}"
        )
        sys.exit(1)
    else:
        logger.error(
            f"Configuration error (non-critical in '{env_for_error_handling_raw}' environment): {e}"
        )
        raise
except Exception as e:
    env_for_error_handling_raw = (
        os.getenv("ENVIRONMENT", Environment.DEVELOPMENT.value).strip().lower()
    )
    is_prod_or_staging_for_error = env_for_error_handling_raw in (
        Environment.PRODUCTION.value,
        Environment.STAGING.value,
    )
    logger.critical(
        f"FATAL: An unexpected error occurred while loading application settings in '{env_for_error_handling_raw}' environment: {e}"
    )
    if is_prod_or_staging_for_error:
        sys.exit(1)
    else:
        raise

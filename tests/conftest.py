"""
Test fixtures for the OpenAI API Blueprint.
"""

import pytest
from fastapi.testclient import TestClient

from openai_api_blueprint.main import app


@pytest.fixture
def client():
    """
    Create a test client for the FastAPI app.

    Returns:
        TestClient: A test client that can be used to send requests to the FastAPI app.
    """
    return TestClient(app)

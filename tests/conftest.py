"""Test configuration and fixtures."""

import pytest
import asyncio
from typing import AsyncGenerator
import os
from httpx import AsyncClient
from src.main import app

# Set test environment - mock credentials for testing
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://test.openai.azure.com/"
os.environ["AZURE_OPENAI_API_KEY"] = "test_key_for_testing_only"
os.environ["DEBUG"] = "true"
os.environ["USE_AZURE_CLI"] = "false"  # Disable Azure CLI in tests

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async client for testing."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def sample_url():
    """Sample URL for testing."""
    return "https://example.com"

@pytest.fixture
def sample_urls():
    """Sample URLs for batch testing."""
    return [
        "https://example.com",
        "https://httpbin.org/html",
        "https://wikipedia.org"
    ]
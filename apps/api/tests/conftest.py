"""
Pytest configuration and fixtures for DocGraph API tests
"""
import asyncio
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from src.main import create_app


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_app():
    """Create FastAPI test application."""
    return create_app()


@pytest.fixture
def client(test_app):
    """Create test client for synchronous tests."""
    return TestClient(test_app)


@pytest.fixture
async def async_client(test_app) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client for asynchronous tests."""
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
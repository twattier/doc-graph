"""
Pytest configuration and fixtures for DocGraph API tests
"""
import asyncio
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from src.main import create_app
from src.init_db import init_test_db


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
def test_app_with_auth_override():
    """Create FastAPI test application with authentication override."""
    from unittest.mock import Mock
    from src.routes.users import get_current_user

    app = create_app()

    # Create mock user
    def override_get_current_user():
        mock_user = Mock()
        mock_user.id = "user123"
        mock_user.email = "test@example.com"
        return mock_user

    # Override the dependency
    app.dependency_overrides[get_current_user] = override_get_current_user

    return app


@pytest.fixture
def client(test_app):
    """Create test client for synchronous tests."""
    return TestClient(test_app)


@pytest.fixture
def client_with_auth(test_app_with_auth_override):
    """Create test client with authentication overridden."""
    return TestClient(test_app_with_auth_override)


@pytest.fixture(scope="session", autouse=True)
async def setup_test_database():
    """Initialize test database before running tests."""
    try:
        await init_test_db()
    except Exception as e:
        pytest.skip(f"Could not initialize test database: {e}")


@pytest.fixture
def async_client(test_app):
    """Create async test client for asynchronous tests."""
    transport = ASGITransport(app=test_app)
    return AsyncClient(transport=transport, base_url="http://test")
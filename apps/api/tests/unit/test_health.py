"""
Unit tests for health check endpoints
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
def test_health_check_endpoint_exists(client: TestClient):
    """Test that health check endpoint exists and returns a response."""
    response = client.get("/health")

    # Should return some response (may be unhealthy due to missing services in test)
    assert response.status_code in [200, 503]
    assert "status" in response.json()


@pytest.mark.unit
def test_health_check_response_structure(client: TestClient):
    """Test that health check response has the expected structure."""
    response = client.get("/health")
    data = response.json()

    # Check required fields
    assert "status" in data
    assert "timestamp" in data
    assert "version" in data

    # Status should be either healthy or unhealthy
    assert data["status"] in ["healthy", "unhealthy"]


@pytest.mark.unit
def test_health_check_version(client: TestClient):
    """Test that health check returns the correct API version."""
    response = client.get("/health")
    data = response.json()

    assert data["version"] == "0.1.0"


@pytest.mark.unit
def test_health_check_error_handling(client: TestClient):
    """Test that health check handles service errors gracefully."""
    response = client.get("/health")

    # Should return a response even if services are unavailable
    assert response.status_code in [200, 503]

    data = response.json()

    # Should not expose internal error details in production
    if "error" in data:
        assert "password" not in data["error"].lower()
        assert "secret" not in data["error"].lower()
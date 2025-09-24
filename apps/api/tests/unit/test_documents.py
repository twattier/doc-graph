"""
Unit tests for document endpoints
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
def test_list_documents(client: TestClient):
    """Test listing documents endpoint."""
    response = client.get("/api/documents")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Should have mock documents
    assert len(data) >= 0


@pytest.mark.unit
def test_get_document_success(client: TestClient):
    """Test getting a specific document that exists."""
    response = client.get("/api/documents/1")

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "title" in data
    assert "content" in data
    assert "file_type" in data
    assert data["id"] == "1"


@pytest.mark.unit
def test_get_document_not_found(client: TestClient):
    """Test getting a document that doesn't exist."""
    response = client.get("/api/documents/nonexistent")

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


@pytest.mark.unit
def test_create_document(client: TestClient):
    """Test creating a new document."""
    document_data = {
        "title": "Test Document",
        "content": "This is a test document.",
        "file_type": "text"
    }

    response = client.post("/api/documents", json=document_data)

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == document_data["title"]
    assert data["content"] == document_data["content"]
    assert data["file_type"] == document_data["file_type"]


@pytest.mark.unit
def test_create_document_invalid_data(client: TestClient):
    """Test creating a document with invalid data."""
    invalid_data = {
        "title": "",  # Empty title should be invalid
        "content": "Content"
    }

    response = client.post("/api/documents", json=invalid_data)

    # Should validate input and return error
    assert response.status_code == 422
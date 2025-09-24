"""
Unit tests for Repository API routes - Story 1.2 Git Repository Import System
"""
import pytest
import uuid
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import HTTPException

from src.models.repository import ImportJob, Repository, RepositoryImportRequest


class TestRepositoryRoutes:
    """Test suite for repository API endpoints."""

    @pytest.mark.unit
    def test_import_repository_valid_request(self, client_with_auth):
        """Test repository import with valid request data."""
        # Mock all the services and dependencies
        with patch('src.routes.repositories.apply_rate_limit') as mock_rate_limit, \
             patch('src.routes.repositories.git_service') as mock_git_service, \
             patch('src.routes.repositories.get_async_db') as mock_db:

            # Mock rate limiting
            mock_rate_limit.return_value = None

            # Mock git service
            mock_git_service.validate_repository_url.return_value = True

            # Mock database session
            mock_session = AsyncMock()
            mock_db.return_value.__anext__.return_value = mock_session

            response = client_with_auth.post(
                "/api/repositories/import",
                json={
                    "url": "https://github.com/test/repo.git"
                },
                headers={"Authorization": "Bearer test-token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert "import_id" in data
            assert "message" in data

    @pytest.mark.unit
    def test_import_repository_invalid_url(self, client: TestClient):
        """Test repository import with invalid URL."""
        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_user = Mock()
            mock_user.id = "user123"
            mock_user.email = "test@example.com"
            mock_auth.return_value = mock_user

            response = client.post(
                "/api/repositories/import",
                json={
                    "url": "invalid-url",
                    "name": "Test Repository"
                },
                headers={"Authorization": "Bearer test-token"}
            )

            assert response.status_code == 422
            assert "validation error" in response.json()["detail"][0]["msg"].lower()

    @pytest.mark.unit
    def test_import_repository_unauthorized(self, client: TestClient):
        """Test repository import without authentication."""
        response = client.post(
            "/api/repositories/import",
            json={
                "url": "https://github.com/test/repo.git",
                "name": "Test Repository"
            }
        )

        assert response.status_code == 401

    @pytest.mark.unit
    def test_get_import_status_success(self, client: TestClient):
        """Test getting import status for existing job."""
        job_id = str(uuid.uuid4())

        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_user = Mock()
            mock_user.id = "user123"
            mock_user.email = "test@example.com"
            mock_auth.return_value = mock_user

            with patch('src.routes.repositories.RepositoryService') as mock_service:
                mock_import_job = {
                    "id": job_id,
                    "status": "in_progress",
                    "progress": 50,
                    "message": "Cloning repository..."
                }
                mock_service.return_value.get_import_status.return_value = mock_import_job

                response = client.get(
                    f"/api/repositories/import/{job_id}/status",
                    headers={"Authorization": "Bearer test-token"}
                )

                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "in_progress"
                assert data["progress"] == 50

    @pytest.mark.unit
    def test_get_import_status_not_found(self, client: TestClient):
        """Test getting import status for non-existent job."""
        job_id = str(uuid.uuid4())

        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_user = Mock()
            mock_user.id = "user123"
            mock_user.email = "test@example.com"
            mock_auth.return_value = mock_user

            with patch('src.routes.repositories.RepositoryService') as mock_service:
                mock_service.return_value.get_import_status.return_value = None

                response = client.get(
                    f"/api/repositories/import/{job_id}/status",
                    headers={"Authorization": "Bearer test-token"}
                )

                assert response.status_code == 404

    @pytest.mark.unit
    def test_list_repositories_success(self, client: TestClient):
        """Test listing user repositories."""
        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_user = Mock()
            mock_user.id = "user123"
            mock_user.email = "test@example.com"
            mock_auth.return_value = mock_user

            with patch('src.routes.repositories.RepositoryService') as mock_service:
                mock_repositories = [
                    {
                        "id": str(uuid.uuid4()),
                        "name": "Test Repo 1",
                        "repository_url": "https://github.com/test/repo1.git",
                        "status": "completed",
                        "user_id": "user123"
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "name": "Test Repo 2",
                        "repository_url": "https://github.com/test/repo2.git",
                        "status": "completed",
                        "user_id": "user123"
                    }
                ]
                mock_service.return_value.list_user_repositories.return_value = mock_repositories

                response = client.get(
                    "/api/repositories",
                    headers={"Authorization": "Bearer test-token"}
                )

                assert response.status_code == 200
                data = response.json()
                assert len(data) == 2
                assert data[0]["name"] == "Test Repo 1"
                assert data[1]["name"] == "Test Repo 2"

    @pytest.mark.unit
    def test_get_repository_success(self, client: TestClient):
        """Test getting specific repository details."""
        repo_id = str(uuid.uuid4())

        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_user = Mock()
            mock_user.id = "user123"
            mock_user.email = "test@example.com"
            mock_auth.return_value = mock_user

            with patch('src.routes.repositories.RepositoryService') as mock_service:
                mock_repository = {
                    "id": repo_id,
                    "name": "Test Repository",
                    "url": "https://github.com/test/repo.git",
                    "status": "completed",
                    "user_id": "user123",
                    "file_count": 25,
                    "total_size": 1024000
                }
                mock_service.return_value.get_repository.return_value = mock_repository

                response = client.get(
                    f"/api/repositories/{repo_id}",
                    headers={"Authorization": "Bearer test-token"}
                )

                assert response.status_code == 200
                data = response.json()
                assert data["id"] == repo_id
                assert data["name"] == "Test Repository"
                assert data["file_count"] == 25

    @pytest.mark.unit
    def test_get_repository_not_found(self, client: TestClient):
        """Test getting non-existent repository."""
        repo_id = str(uuid.uuid4())

        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_user = Mock()
            mock_user.id = "user123"
            mock_user.email = "test@example.com"
            mock_auth.return_value = mock_user

            with patch('src.routes.repositories.RepositoryService') as mock_service:
                mock_service.return_value.get_repository.return_value = None

                response = client.get(
                    f"/api/repositories/{repo_id}",
                    headers={"Authorization": "Bearer test-token"}
                )

                assert response.status_code == 404

    @pytest.mark.unit
    def test_delete_repository_success(self, client: TestClient):
        """Test deleting repository."""
        repo_id = str(uuid.uuid4())

        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_user = Mock()
            mock_user.id = "user123"
            mock_user.email = "test@example.com"
            mock_auth.return_value = mock_user

            with patch('src.routes.repositories.RepositoryService') as mock_service:
                mock_service.return_value.delete_repository.return_value = True

                response = client.delete(
                    f"/api/repositories/{repo_id}",
                    headers={"Authorization": "Bearer test-token"}
                )

                assert response.status_code == 204

    @pytest.mark.unit
    def test_sync_repository_success(self, client: TestClient):
        """Test synchronizing repository updates."""
        repo_id = str(uuid.uuid4())

        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_user = Mock()
            mock_user.id = "user123"
            mock_user.email = "test@example.com"
            mock_auth.return_value = mock_user

            with patch('src.routes.repositories.RepositoryService') as mock_service:
                mock_sync_job = {
                    "id": str(uuid.uuid4()),
                    "repository_id": repo_id,
                    "status": "pending",
                    "type": "sync"
                }
                mock_service.return_value.sync_repository.return_value = mock_sync_job

                response = client.put(
                    f"/api/repositories/{repo_id}/sync",
                    headers={"Authorization": "Bearer test-token"}
                )

                assert response.status_code == 202
                data = response.json()
                assert data["status"] == "pending"
                assert data["type"] == "sync"

    @pytest.mark.unit
    def test_repository_url_validation_in_request_model(self):
        """Test repository URL validation in Pydantic model."""
        # Test valid URL
        valid_request = RepositoryImportRequest(
            repository_url="https://github.com/test/repo.git",
            name="Test Repo"
        )
        assert valid_request.repository_url == "https://github.com/test/repo.git"

        # Test invalid URL should raise validation error
        with pytest.raises(Exception):  # Pydantic validation error
            RepositoryImportRequest(
                repository_url="not-a-valid-url",
                name="Test Repo"
            )
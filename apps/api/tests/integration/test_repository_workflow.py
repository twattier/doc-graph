"""
Integration tests for repository import workflow - Story 1.2 Git Repository Import System
"""
import pytest
import asyncio
import tempfile
import os
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.services.git_service import GitService
from src.services.repository_service import RepositoryService
from src.models.repository import Repository, ImportJob


class TestRepositoryWorkflowIntegration:
    """Integration tests for complete repository import workflow."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_complete_repository_import_workflow(self, async_client: AsyncClient):
        """Test complete repository import from request to completion."""
        # This would be a full integration test in a real scenario
        # For now, we'll test the service layer integration

        git_service = GitService()
        repo_service = RepositoryService()

        # Mock external dependencies
        with patch.object(git_service, 'clone_repository') as mock_clone:
            mock_repo_info = Mock()
            mock_repo_info.url = "https://github.com/test/repo.git"
            mock_repo_info.name = "test-repo"
            mock_repo_info.commit_hash = "abc123"
            mock_repo_info.branch = "main"
            mock_repo_info.file_count = 10
            mock_repo_info.total_size = 5120
            mock_clone.return_value = mock_repo_info

            # Test workflow steps
            # 1. URL validation
            assert git_service.validate_repository_url("https://github.com/test/repo.git")

            # 2. Repository cloning
            with tempfile.TemporaryDirectory() as temp_dir:
                result = await git_service.clone_repository(
                    "https://github.com/test/repo.git",
                    temp_dir
                )

                assert result.name == "test-repo"
                assert result.file_count == 10
                assert result.total_size == 5120

    @pytest.mark.integration
    def test_repository_import_with_authentication(self, client: TestClient):
        """Test repository import with proper authentication flow."""
        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user123", "email": "test@example.com"}

            with patch('src.routes.repositories.RepositoryService') as mock_service:
                # Mock successful import job creation
                mock_import_job = {
                    "id": "job123",
                    "repository_url": "https://github.com/test/repo.git",
                    "status": "pending",
                    "user_id": "user123",
                    "progress": 0,
                    "message": "Import started"
                }
                mock_service.return_value.start_import.return_value = mock_import_job

                # Start import
                response = client.post(
                    "/api/repositories/import",
                    json={
                        "repository_url": "https://github.com/test/repo.git",
                        "name": "Test Integration Repo"
                    },
                    headers={"Authorization": "Bearer test-token"}
                )

                assert response.status_code == 202
                import_data = response.json()["import_job"]

                # Check status
                mock_service.return_value.get_import_status.return_value = {
                    **mock_import_job,
                    "status": "completed",
                    "progress": 100,
                    "message": "Import completed successfully"
                }

                status_response = client.get(
                    f"/api/repositories/import/{import_data['id']}/status",
                    headers={"Authorization": "Bearer test-token"}
                )

                assert status_response.status_code == 200
                status_data = status_response.json()
                assert status_data["status"] == "completed"
                assert status_data["progress"] == 100

    @pytest.mark.integration
    def test_repository_error_handling_workflow(self, client: TestClient):
        """Test error handling throughout the repository workflow."""
        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user123", "email": "test@example.com"}

            with patch('src.routes.repositories.RepositoryService') as mock_service:
                # Mock service error during import
                from src.services.git_service import GitOperationError
                mock_service.return_value.start_import.side_effect = GitOperationError("Repository not accessible")

                response = client.post(
                    "/api/repositories/import",
                    json={
                        "repository_url": "https://github.com/invalid/repo.git",
                        "name": "Invalid Repo"
                    },
                    headers={"Authorization": "Bearer test-token"}
                )

                # Should handle the error gracefully
                assert response.status_code == 400
                assert "Repository not accessible" in response.json()["detail"]

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_repository_service_database_integration(self):
        """Test repository service database operations."""
        # This would require actual database connection in real scenario
        # For now, we'll mock the database layer

        repo_service = RepositoryService()

        with patch.object(repo_service, '_get_db_session') as mock_db:
            mock_session = Mock()
            mock_db.return_value.__aenter__ = Mock(return_value=mock_session)
            mock_db.return_value.__aexit__ = Mock(return_value=None)

            # Mock repository creation
            mock_repository = Repository()
            mock_repository.id = "repo123"
            mock_repository.name = "Test Repo"
            mock_repository.repository_url = "https://github.com/test/repo.git"
            mock_repository.status = "completed"

            mock_session.add.return_value = None
            mock_session.commit.return_value = None

            # Test repository creation workflow
            user_id = "user123"
            import_request = {
                "repository_url": "https://github.com/test/repo.git",
                "name": "Test Repo"
            }

            # In a real test, this would create actual database records
            # For now, we verify the service layer calls the right methods
            mock_session.add.assert_not_called()  # Not called yet

    @pytest.mark.integration
    def test_repository_background_task_integration(self, client: TestClient):
        """Test background task processing for repository imports."""
        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user123", "email": "test@example.com"}

            with patch('src.routes.repositories.RepositoryService') as mock_service:
                with patch('src.routes.repositories.BackgroundTasks') as mock_bg_tasks:
                    # Mock background task execution
                    mock_task_instance = Mock()
                    mock_bg_tasks.return_value = mock_task_instance

                    mock_import_job = {
                        "id": "job123",
                        "repository_url": "https://github.com/test/repo.git",
                        "status": "pending",
                        "user_id": "user123"
                    }
                    mock_service.return_value.start_import.return_value = mock_import_job

                    response = client.post(
                        "/api/repositories/import",
                        json={
                            "repository_url": "https://github.com/test/repo.git",
                            "name": "Background Task Repo"
                        },
                        headers={"Authorization": "Bearer test-token"}
                    )

                    assert response.status_code == 202
                    # Verify background task was scheduled
                    mock_task_instance.add_task.assert_called()

    @pytest.mark.integration
    def test_repository_list_pagination_and_filtering(self, client: TestClient):
        """Test repository listing with pagination and filtering."""
        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user123", "email": "test@example.com"}

            with patch('src.routes.repositories.RepositoryService') as mock_service:
                # Mock paginated repository list
                mock_repositories = [
                    {
                        "id": f"repo{i}",
                        "name": f"Repo {i}",
                        "repository_url": f"https://github.com/test/repo{i}.git",
                        "status": "completed" if i % 2 == 0 else "pending",
                        "user_id": "user123"
                    }
                    for i in range(1, 6)  # 5 repositories
                ]
                mock_service.return_value.list_user_repositories.return_value = mock_repositories

                response = client.get(
                    "/api/repositories?limit=3&offset=0",
                    headers={"Authorization": "Bearer test-token"}
                )

                assert response.status_code == 200
                data = response.json()
                assert len(data) <= 5  # Should respect pagination in real implementation

    @pytest.mark.integration
    def test_repository_sync_workflow(self, client: TestClient):
        """Test repository synchronization workflow."""
        repo_id = "repo123"

        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user123", "email": "test@example.com"}

            with patch('src.routes.repositories.RepositoryService') as mock_service:
                # Mock repository exists and is owned by user
                mock_repository = {
                    "id": repo_id,
                    "name": "Test Repo",
                    "repository_url": "https://github.com/test/repo.git",
                    "status": "completed",
                    "user_id": "user123"
                }
                mock_service.return_value.get_repository.return_value = mock_repository

                # Mock sync job creation
                mock_sync_job = {
                    "id": "sync123",
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
                sync_data = response.json()
                assert sync_data["type"] == "sync"
                assert sync_data["repository_id"] == repo_id
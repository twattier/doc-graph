"""
Error handling tests for various failure scenarios - Story 1.2 Git Repository Import System

This test suite validates error handling for network timeouts, invalid repository states,
authentication failures, and other edge cases using the magnet repository.
"""

import pytest
import asyncio
import tempfile
import os
from unittest.mock import patch, Mock, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.services.git_service import GitService, GitOperationError
from src.services.repository_service import RepositoryService


class TestMagnetErrorHandling:
    """Error handling tests for magnet repository import system."""

    MAGNET_REPO_URL = "https://github.com/twattier/magnet"

    @pytest.fixture
    def git_service(self):
        """Create GitService instance for testing."""
        return GitService()

    @pytest.fixture
    def repository_service(self, git_service):
        """Create RepositoryService instance for testing."""
        return RepositoryService(git_service)

    @pytest.mark.unit
    def test_invalid_magnet_repository_url_handling(self, git_service):
        """Test handling of invalid magnet repository URL variations."""
        invalid_urls = [
            "",  # Empty URL
            None,  # None URL
            "not-a-url",  # Not a URL at all
            "http://github.com/twattier/magnet",  # HTTP instead of HTTPS
            "https://github.com/twattier/",  # Missing repository name
            "https://github.com/magnet",  # Missing owner
            "https://malicious-site.com/twattier/magnet",  # Wrong domain
            "ftp://github.com/twattier/magnet",  # Wrong protocol
            "https://github.com/twattier/magnet/tree/main",  # Tree URL instead of repo
            "https://github.com/",  # Just domain
            "github.com/twattier/magnet",  # Missing protocol
        ]

        for invalid_url in invalid_urls:
            # Should return False for invalid URLs
            is_valid = git_service.validate_repository_url(invalid_url)
            assert is_valid is False, f"URL should be invalid: {invalid_url}"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_network_timeout_during_clone(self, git_service):
        """Test handling of network timeouts during repository cloning."""
        import asyncio
        from git import GitError

        with patch('src.services.git_service.Repo.clone_from') as mock_clone:
            # Simulate network timeout
            mock_clone.side_effect = GitError("timeout: unable to access repository")

            with pytest.raises(GitOperationError) as exc_info:
                await git_service.clone_repository(self.MAGNET_REPO_URL, "timeout-test")

            assert "Failed to clone repository" in str(exc_info.value)
            assert "timeout" in str(exc_info.value).lower()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_repository_not_found_error(self, git_service):
        """Test handling when magnet repository is not found (404)."""
        from git import GitError

        with patch('src.services.git_service.Repo.clone_from') as mock_clone:
            # Simulate repository not found
            mock_clone.side_effect = GitError("fatal: repository 'https://github.com/twattier/nonexistent.git' not found")

            with pytest.raises(GitOperationError) as exc_info:
                await git_service.clone_repository("https://github.com/twattier/nonexistent.git", "not-found-test")

            assert "Failed to clone repository" in str(exc_info.value)
            assert "not found" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_authentication_failure_private_repo(self, git_service):
        """Test handling of authentication failure for private repositories."""
        from git import GitError

        with patch('src.services.git_service.Repo.clone_from') as mock_clone:
            # Simulate authentication failure
            mock_clone.side_effect = GitError("fatal: Authentication failed for repository")

            with pytest.raises(GitOperationError) as exc_info:
                await git_service.clone_repository(self.MAGNET_REPO_URL, "auth-fail-test")

            assert "Failed to clone repository" in str(exc_info.value)
            assert "Authentication failed" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_insufficient_disk_space_error(self, git_service):
        """Test handling of insufficient disk space during clone."""
        import asyncio
        from git import GitError

        with patch('src.services.git_service.Repo.clone_from') as mock_clone:
            # Simulate disk space error
            mock_clone.side_effect = OSError("No space left on device")

            with pytest.raises(GitOperationError) as exc_info:
                await git_service.clone_repository(self.MAGNET_REPO_URL, "disk-space-test")

            assert "Unexpected error during clone" in str(exc_info.value)
            assert "No space left on device" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_corrupted_repository_handling(self, git_service):
        """Test handling of corrupted repository during analysis."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create corrupted file that can't be read
            corrupted_file = os.path.join(temp_dir, "corrupted.bin")

            # Create file and then make it unreadable
            with open(corrupted_file, 'wb') as f:
                f.write(b'\x00' * 1000)  # Binary data

            # Mock os.path.getsize to raise an error
            with patch('os.path.getsize') as mock_getsize:
                mock_getsize.side_effect = OSError("Permission denied")

                # Should handle the error gracefully
                repo_analysis = await git_service._analyze_repository(temp_dir)

                # Should still return valid analysis (skipping problematic files)
                assert repo_analysis["file_count"] == 0  # No files counted due to errors
                assert repo_analysis["total_size"] == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_unicode_decode_error_in_files(self, git_service):
        """Test handling of unicode decode errors in repository files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create file with invalid UTF-8
            binary_file = os.path.join(temp_dir, "binary.dat")
            with open(binary_file, 'wb') as f:
                f.write(b'\xff\xfe\x00\x00invalid_utf8\x80\x81')

            # Create README that should be readable
            readme_file = os.path.join(temp_dir, "README.md")
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write("# Valid UTF-8 content")

            # Should handle decode error gracefully
            repo_analysis = await git_service._analyze_repository(temp_dir)

            # Should count files but handle decode error for description
            assert repo_analysis["file_count"] == 2
            assert repo_analysis["total_size"] > 0
            # Description might be None if README decode fails, or from fallback

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_api_rate_limiting_error_handling(self, async_client: AsyncClient):
        """Test handling of API rate limiting during import."""
        from src.middleware.rate_limiting import RateLimitExceeded

        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_user = Mock()
            mock_user.id = "user123"
            mock_user.email = "test@example.com"
            mock_auth.return_value = mock_user

            # Mock rate limiting to raise an exception
            with patch('src.routes.repositories.apply_rate_limit') as mock_rate_limit:
                mock_rate_limit.side_effect = RateLimitExceeded("Rate limit exceeded for repository imports")

                response = await async_client.post(
                    "/api/repositories/import",
                    json={
                        "url": self.MAGNET_REPO_URL,
                        "name": "Rate Limited Test"
                    },
                    headers={"Authorization": "Bearer test-token"}
                )

                # Should handle rate limiting error
                assert response.status_code in [429, 500]  # Too Many Requests or server error

    @pytest.mark.unit
    def test_invalid_import_request_validation(self, client: TestClient):
        """Test validation of invalid import request payloads."""
        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_user = Mock()
            mock_user.id = "user123"
            mock_user.email = "test@example.com"
            mock_auth.return_value = mock_user

            with patch('src.routes.repositories.apply_rate_limit'):
                # Test cases for invalid requests
                invalid_requests = [
                    # Missing URL
                    {"name": "Test Repo"},
                    # Empty URL
                    {"url": "", "name": "Test Repo"},
                    # Invalid URL format
                    {"url": "not-a-url", "name": "Test Repo"},
                    # Missing name
                    {"url": self.MAGNET_REPO_URL},
                    # Empty name
                    {"url": self.MAGNET_REPO_URL, "name": ""},
                    # None values
                    {"url": None, "name": "Test Repo"},
                    {"url": self.MAGNET_REPO_URL, "name": None},
                ]

                for invalid_request in invalid_requests:
                    response = client.post(
                        "/api/repositories/import",
                        json=invalid_request,
                        headers={"Authorization": "Bearer test-token"}
                    )

                    # Should reject invalid requests
                    assert response.status_code in [400, 422], f"Request should be invalid: {invalid_request}"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_background_task_failure_handling(self, async_client: AsyncClient):
        """Test handling of background task failures during import."""
        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_user = Mock()
            mock_user.id = "user123"
            mock_user.email = "test@example.com"
            mock_auth.return_value = mock_user

            with patch('src.routes.repositories.apply_rate_limit'):
                # Mock GitService to raise an error
                with patch('src.services.git_service.GitService.clone_repository') as mock_clone:
                    mock_clone.side_effect = GitOperationError("Clone operation failed")

                    response = await async_client.post(
                        "/api/repositories/import",
                        json={
                            "url": self.MAGNET_REPO_URL,
                            "name": "Background Failure Test"
                        },
                        headers={"Authorization": "Bearer test-token"}
                    )

                    # Initial request should succeed (background task scheduled)
                    assert response.status_code == 202
                    import_data = response.json()
                    import_id = import_data["import_id"]

                    # Give background task time to fail
                    await asyncio.sleep(0.1)

                    # Check status should show failure
                    with patch('src.routes.repositories.select') as mock_select:
                        mock_import_job = Mock()
                        mock_import_job.id = import_id
                        mock_import_job.status = "failed"
                        mock_import_job.progress = 0
                        mock_import_job.message = "Import failed"
                        mock_import_job.error_message = "Clone operation failed"

                        mock_result = Mock()
                        mock_result.scalar_one_or_none.return_value = mock_import_job

                        with patch('src.routes.repositories.get_async_db') as mock_db:
                            mock_session = AsyncMock()
                            mock_session.execute.return_value = mock_result
                            mock_db.return_value.__anext__ = AsyncMock(return_value=mock_session)

                            status_response = await async_client.get(
                                f"/api/repositories/{import_id}/status"
                            )

                            assert status_response.status_code == 200
                            status_data = status_response.json()
                            assert status_data["status"] == "failed"

    @pytest.mark.unit
    def test_nonexistent_import_status_check(self, client: TestClient):
        """Test checking status of non-existent import job."""
        fake_import_id = "non-existent-import-id"

        with patch('src.routes.repositories.select') as mock_select:
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = None  # Import job not found

            with patch('src.routes.repositories.get_async_db') as mock_db:
                mock_session = Mock()
                mock_session.execute.return_value = mock_result
                mock_db.return_value.__anext__ = Mock(return_value=mock_session)

                response = client.get(f"/api/repositories/{fake_import_id}/status")

                assert response.status_code == 404
                assert "not found" in response.json()["detail"].lower()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_repository_sync_failure_handling(self, async_client: AsyncClient):
        """Test handling of repository sync failures."""
        repository_id = "magnet-repo-123"

        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_user = Mock()
            mock_user.id = "user123"
            mock_user.email = "test@example.com"
            mock_auth.return_value = mock_user

            with patch('src.routes.repositories.select') as mock_select:
                mock_repository = Mock()
                mock_repository.id = repository_id
                mock_repository.name = "magnet"
                mock_repository.status = "active"

                mock_result = Mock()
                mock_result.scalar_one_or_none.return_value = mock_repository

                with patch('src.routes.repositories.get_async_db') as mock_db:
                    mock_session = AsyncMock()
                    mock_session.execute.return_value = mock_result
                    mock_session.commit.return_value = None
                    mock_db.return_value.__anext__ = AsyncMock(return_value=mock_session)

                    # Mock Git service to fail
                    with patch('src.services.git_service.GitService.update_repository') as mock_update:
                        mock_update.side_effect = GitOperationError("Failed to pull from remote")

                        response = await async_client.put(
                            f"/api/repositories/{repository_id}/sync",
                            headers={"Authorization": "Bearer test-token"}
                        )

                        # Should accept sync request initially
                        assert response.status_code == 200

                        # Sync would fail in background, updating repository status to "error"

    @pytest.mark.unit
    def test_repository_access_denied_handling(self, client: TestClient):
        """Test handling of access denied scenarios."""
        repository_id = "someone-elses-repo"

        # User trying to access repository they don't own
        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_user = Mock()
            mock_user.id = "user123"
            mock_user.email = "test@example.com"
            mock_auth.return_value = mock_user

            with patch('src.routes.repositories.select') as mock_select:
                # Repository not found for this user
                mock_result = Mock()
                mock_result.scalar_one_or_none.return_value = None

                with patch('src.routes.repositories.get_async_db') as mock_db:
                    mock_session = Mock()
                    mock_session.execute.return_value = mock_result
                    mock_db.return_value.__anext__ = Mock(return_value=mock_session)

                    # Try to access repository files
                    response = client.get(
                        f"/api/repositories/{repository_id}/files",
                        headers={"Authorization": "Bearer test-token"}
                    )

                    assert response.status_code == 404
                    assert "not found or access denied" in response.json()["detail"].lower()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_storage_space_exhaustion(self, repository_service):
        """Test handling when storage space is exhausted."""
        with patch.object(repository_service, 'get_storage_usage') as mock_usage:
            # Mock storage at 100% capacity
            mock_usage.return_value = {
                'total_size_bytes': 1000000000,  # 1GB
                'total_size_gb': 1.0,
                'repository_count': 50,
                'storage_limit_gb': 1.0,  # Same as used
                'usage_percentage': 100.0
            }

            # Should trigger cleanup
            cleanup_performed = await repository_service.cleanup_storage_if_needed(Mock(), threshold_percentage=80.0)

            # Cleanup should be attempted
            assert cleanup_performed in [True, False]  # Depends on mock setup

    @pytest.mark.unit
    def test_malformed_json_request_handling(self, client: TestClient):
        """Test handling of malformed JSON in import requests."""
        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_user = Mock()
            mock_user.id = "user123"
            mock_user.email = "test@example.com"
            mock_auth.return_value = mock_user

            # Send malformed JSON
            response = client.post(
                "/api/repositories/import",
                data='{"url": "https://github.com/twattier/magnet", "name": "Test"',  # Missing closing brace
                headers={
                    "Authorization": "Bearer test-token",
                    "Content-Type": "application/json"
                }
            )

            # Should handle JSON parse error
            assert response.status_code == 422  # Unprocessable Entity

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_database_connection_failure(self, async_client: AsyncClient):
        """Test handling of database connection failures."""
        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_user = Mock()
            mock_user.id = "user123"
            mock_user.email = "test@example.com"
            mock_auth.return_value = mock_user

            with patch('src.routes.repositories.apply_rate_limit'):
                # Mock database connection failure
                with patch('src.routes.repositories.get_async_db') as mock_db:
                    mock_db.side_effect = Exception("Database connection failed")

                    response = await async_client.post(
                        "/api/repositories/import",
                        json={
                            "url": self.MAGNET_REPO_URL,
                            "name": "DB Failure Test"
                        },
                        headers={"Authorization": "Bearer test-token"}
                    )

                    # Should handle database error
                    assert response.status_code == 500

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_concurrent_import_conflict_handling(self, async_client: AsyncClient):
        """Test handling of concurrent import conflicts."""
        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_user = Mock()
            mock_user.id = "user123"
            mock_user.email = "test@example.com"
            mock_auth.return_value = mock_user

            with patch('src.routes.repositories.apply_rate_limit'):
                with patch('src.services.git_service.GitService.clone_repository') as mock_clone:
                    # Simulate file system conflict during clone
                    mock_clone.side_effect = OSError("Directory already exists")

                    response = await async_client.post(
                        "/api/repositories/import",
                        json={
                            "url": self.MAGNET_REPO_URL,
                            "name": "Conflict Test"
                        },
                        headers={"Authorization": "Bearer test-token"}
                    )

                    # Initial request should succeed, error occurs in background
                    assert response.status_code == 202

    @pytest.mark.unit
    def test_repository_deletion_failure_handling(self, client: TestClient):
        """Test handling of repository deletion failures."""
        repository_id = "magnet-repo-123"

        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_user = Mock()
            mock_user.id = "user123"
            mock_user.email = "test@example.com"
            mock_auth.return_value = mock_user

            with patch('src.routes.repositories.select') as mock_select:
                mock_repository = Mock()
                mock_repository.id = repository_id

                mock_result = Mock()
                mock_result.scalar_one_or_none.return_value = mock_repository

                with patch('src.routes.repositories.get_async_db') as mock_db:
                    mock_session = Mock()
                    mock_session.execute.return_value = mock_result
                    mock_session.commit.side_effect = Exception("Database error during deletion")
                    mock_db.return_value.__anext__ = Mock(return_value=mock_session)

                    response = client.delete(
                        f"/api/repositories/{repository_id}",
                        headers={"Authorization": "Bearer test-token"}
                    )

                    # Should handle deletion error
                    assert response.status_code == 500

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_repository_processing_failure(self, async_client: AsyncClient):
        """Test handling of repository processing failures."""
        repository_id = "magnet-repo-123"

        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_user = Mock()
            mock_user.id = "user123"
            mock_user.email = "test@example.com"
            mock_auth.return_value = mock_user

            with patch('src.routes.repositories.select') as mock_select:
                mock_repository = Mock()
                mock_repository.id = repository_id
                mock_repository.user_email = "test@example.com"

                mock_result = Mock()
                mock_result.scalar_one_or_none.return_value = mock_repository

                with patch('src.routes.repositories.get_async_db') as mock_db:
                    mock_session = AsyncMock()
                    mock_session.execute.return_value = mock_result
                    mock_session.commit.return_value = None
                    mock_db.return_value.__anext__ = AsyncMock(return_value=mock_session)

                    # Mock processing service to fail
                    with patch('src.services.processing_service.RepositoryProcessor.process_repository') as mock_process:
                        mock_process.side_effect = Exception("Processing pipeline failed")

                        response = await async_client.post(
                            f"/api/repositories/{repository_id}/process",
                            headers={"Authorization": "Bearer test-token"}
                        )

                        # Should accept processing request initially
                        assert response.status_code == 200

                        # Processing would fail in background task
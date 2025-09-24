"""
End-to-end tests for the complete user journey with magnet repository - Story 1.2 Git Repository Import System

This test suite validates the full user experience from registration/login through repository
import, processing, and file browsing using the magnet repository.
"""

import pytest
import asyncio
import time
from unittest.mock import patch, Mock, AsyncMock
from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.services.git_service import GitRepositoryInfo


class TestMagnetUserJourneyE2E:
    """End-to-end tests for complete user journey with magnet repository."""

    MAGNET_REPO_URL = "https://github.com/twattier/magnet"

    @pytest.fixture
    def mock_user(self):
        """Mock user for authentication."""
        return {
            "id": "user123",
            "email": "magnet.tester@example.com",
            "username": "magnet_tester",
            "created_at": "2024-01-01T00:00:00Z"
        }

    @pytest.fixture
    def mock_magnet_repo_info(self):
        """Realistic magnet repository information."""
        return GitRepositoryInfo(
            url=self.MAGNET_REPO_URL,
            name="magnet",
            owner="twattier",
            branch="main",
            commit_hash="2c5a9b8f4d3e1a6c9b8f4d3e1a6c9b8f4d3e1a6c",
            description="Magnetorheological fluid simulation toolkit",
            file_count=42,
            total_size=256000  # 250KB
        )

    @pytest.fixture
    def mock_magnet_files(self):
        """Expected file structure for magnet repository."""
        return [
            "README.md",
            "package.json",
            "LICENSE",
            ".gitignore",
            "src/index.js",
            "src/core/magnet.js",
            "src/core/fluid.js",
            "src/utils/math.js",
            "src/utils/physics.js",
            "test/magnet.test.js",
            "test/fluid.test.js",
            "test/utils.test.js",
            "docs/api.md",
            "docs/getting-started.md",
            "examples/basic.js",
            "examples/advanced.js",
            "dist/magnet.min.js",
            "webpack.config.js",
            "babel.config.js",
            ".eslintrc.js"
        ]

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_complete_user_journey_magnet_import(self, async_client: AsyncClient, mock_user, mock_magnet_repo_info):
        """Test the complete user journey from login to repository browsing."""

        # Setup authentication mock
        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_auth.return_value = mock_user

            with patch('src.routes.repositories.apply_rate_limit') as mock_rate_limit:
                mock_rate_limit.return_value = AsyncMock()

                # Mock the GitService operations
                with patch('src.services.git_service.GitService.clone_repository') as mock_clone:
                    mock_clone.return_value = mock_magnet_repo_info

                    # STEP 1: User initiates repository import
                    import_response = await async_client.post(
                        "/api/repositories/import",
                        json={
                            "url": self.MAGNET_REPO_URL,
                            "name": "My Magnet Repository"
                        },
                        headers={"Authorization": "Bearer test-token"}
                    )

                    assert import_response.status_code == 202
                    import_data = import_response.json()
                    assert "import_id" in import_data
                    import_id = import_data["import_id"]

                    # STEP 2: User checks import progress
                    # Simulate checking progress multiple times
                    progress_checks = [
                        {"status": "pending", "progress": 0, "message": "Import request received"},
                        {"status": "cloning", "progress": 30, "message": "Cloning repository..."},
                        {"status": "processing", "progress": 70, "message": "Processing repository data..."},
                        {"status": "completed", "progress": 100, "message": "Repository imported successfully!"}
                    ]

                    for i, expected_progress in enumerate(progress_checks):
                        with patch('src.routes.repositories.select') as mock_select:
                            # Mock import job
                            mock_import_job = Mock()
                            mock_import_job.id = import_id
                            mock_import_job.status = expected_progress["status"]
                            mock_import_job.progress = expected_progress["progress"]
                            mock_import_job.message = expected_progress["message"]
                            mock_import_job.repository_id = "repo123"

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
                                assert status_data["status"] == expected_progress["status"]
                                assert status_data["progress"] == expected_progress["progress"]
                                assert expected_progress["message"] in status_data["message"]

                    # STEP 3: Import completed - user lists repositories
                    with patch('src.routes.repositories.select') as mock_select:
                        # Mock repository listing
                        mock_repository = Mock()
                        mock_repository.id = "repo123"
                        mock_repository.name = "magnet"
                        mock_repository.owner = "twattier"
                        mock_repository.url = self.MAGNET_REPO_URL
                        mock_repository.branch = "main"
                        mock_repository.commit_hash = mock_magnet_repo_info.commit_hash
                        mock_repository.file_count = mock_magnet_repo_info.file_count
                        mock_repository.total_size = mock_magnet_repo_info.total_size
                        mock_repository.status = "active"
                        mock_repository.description = mock_magnet_repo_info.description
                        mock_repository.imported_at = "2024-01-01T12:00:00Z"
                        mock_repository.user_email = mock_user["email"]

                        mock_result = Mock()
                        mock_result.scalars.return_value.all.return_value = [mock_repository]

                        with patch('src.routes.repositories.get_async_db') as mock_db:
                            mock_session = AsyncMock()
                            mock_session.execute.return_value = mock_result
                            mock_db.return_value.__anext__ = AsyncMock(return_value=mock_session)

                            repositories_response = await async_client.get(
                                "/api/repositories",
                                headers={"Authorization": "Bearer test-token"}
                            )

                            assert repositories_response.status_code == 200
                            repositories_data = repositories_response.json()
                            assert len(repositories_data) == 1
                            assert repositories_data[0]["name"] == "magnet"
                            assert repositories_data[0]["url"] == self.MAGNET_REPO_URL

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_magnet_repository_details_and_processing(self, async_client: AsyncClient, mock_user, mock_magnet_repo_info):
        """Test retrieving repository details and processing workflow."""

        repository_id = "magnet-repo-123"

        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_auth.return_value = mock_user

            # STEP 1: Get repository details
            with patch('src.routes.repositories.select') as mock_select:
                mock_repository = Mock()
                mock_repository.id = repository_id
                mock_repository.name = "magnet"
                mock_repository.owner = "twattier"
                mock_repository.url = self.MAGNET_REPO_URL
                mock_repository.branch = "main"
                mock_repository.commit_hash = mock_magnet_repo_info.commit_hash
                mock_repository.file_count = mock_magnet_repo_info.file_count
                mock_repository.total_size = mock_magnet_repo_info.total_size
                mock_repository.status = "active"
                mock_repository.description = mock_magnet_repo_info.description
                mock_repository.user_email = mock_user["email"]

                mock_result = Mock()
                mock_result.scalar_one_or_none.return_value = mock_repository

                with patch('src.routes.repositories.get_async_db') as mock_db:
                    mock_session = AsyncMock()
                    mock_session.execute.return_value = mock_result
                    mock_db.return_value.__anext__ = AsyncMock(return_value=mock_session)

                    details_response = await async_client.get(
                        f"/api/repositories/{repository_id}",
                        headers={"Authorization": "Bearer test-token"}
                    )

                    assert details_response.status_code == 200
                    details_data = details_response.json()
                    assert details_data["name"] == "magnet"
                    assert details_data["owner"] == "twattier"
                    assert details_data["file_count"] == 42

            # STEP 2: Start repository processing
            with patch('src.routes.repositories.select') as mock_select:
                # Mock repository exists and belongs to user
                mock_result = Mock()
                mock_result.scalar_one_or_none.return_value = mock_repository

                with patch('src.routes.repositories.get_async_db') as mock_db:
                    mock_session = AsyncMock()
                    mock_session.execute.return_value = mock_result
                    mock_db.return_value.__anext__ = AsyncMock(return_value=mock_session)

                    with patch('src.services.processing_service.RepositoryProcessor.process_repository') as mock_process:
                        mock_process.return_value = {
                            "processing_stats": {
                                "files_processed": 42,
                                "documentation_files": 3,
                                "code_files": 25,
                                "test_files": 8
                            }
                        }

                        processing_response = await async_client.post(
                            f"/api/repositories/{repository_id}/process",
                            headers={"Authorization": "Bearer test-token"}
                        )

                        assert processing_response.status_code == 200
                        processing_data = processing_response.json()
                        assert "processing_id" in processing_data
                        assert processing_data["repository_id"] == repository_id

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_magnet_repository_file_browsing(self, async_client: AsyncClient, mock_user, mock_magnet_files):
        """Test browsing magnet repository files."""

        repository_id = "magnet-repo-123"

        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_auth.return_value = mock_user

            # Mock repository exists and belongs to user
            with patch('src.routes.repositories.select') as mock_select:
                mock_repository = Mock()
                mock_repository.id = repository_id
                mock_repository.name = "magnet"
                mock_repository.user_email = mock_user["email"]

                mock_result = Mock()
                mock_result.scalar_one_or_none.return_value = mock_repository

                with patch('src.routes.repositories.get_async_db') as mock_db:
                    mock_session = AsyncMock()
                    mock_session.execute.return_value = mock_result
                    mock_db.return_value.__anext__ = AsyncMock(return_value=mock_session)

                    # Mock file listing
                    with patch('src.services.git_service.GitService.get_repository_files') as mock_get_files:
                        mock_get_files.return_value = mock_magnet_files

                        # STEP 1: Browse root directory
                        files_response = await async_client.get(
                            f"/api/repositories/{repository_id}/files",
                            headers={"Authorization": "Bearer test-token"}
                        )

                        assert files_response.status_code == 200
                        files_data = files_response.json()
                        assert files_data["repository_id"] == repository_id
                        assert "files" in files_data
                        assert len(files_data["files"]) == len(mock_magnet_files)
                        assert "README.md" in files_data["files"]
                        assert "package.json" in files_data["files"]
                        assert "src/index.js" in files_data["files"]

                        # STEP 2: Browse specific directory (src)
                        src_files = [f for f in mock_magnet_files if f.startswith("src/")]
                        mock_get_files.return_value = src_files

                        src_response = await async_client.get(
                            f"/api/repositories/{repository_id}/files?path=src",
                            headers={"Authorization": "Bearer test-token"}
                        )

                        assert src_response.status_code == 200
                        src_data = src_response.json()
                        assert src_data["path"] == "src"
                        assert all(f.startswith("src/") for f in src_data["files"])

    @pytest.mark.e2e
    def test_magnet_repository_sync_workflow(self, client: TestClient, mock_user, mock_magnet_repo_info):
        """Test repository synchronization workflow."""

        repository_id = "magnet-repo-123"

        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_auth.return_value = mock_user

            # Mock repository exists
            with patch('src.routes.repositories.select') as mock_select:
                mock_repository = Mock()
                mock_repository.id = repository_id
                mock_repository.name = "magnet"
                mock_repository.url = self.MAGNET_REPO_URL
                mock_repository.status = "active"

                mock_result = Mock()
                mock_result.scalar_one_or_none.return_value = mock_repository

                with patch('src.routes.repositories.get_async_db') as mock_db:
                    mock_session = Mock()
                    mock_session.execute.return_value = mock_result
                    mock_session.commit.return_value = None
                    mock_db.return_value.__anext__ = Mock(return_value=mock_session)

                    # Mock Git service update
                    with patch('src.services.git_service.GitService.update_repository') as mock_update:
                        # Create updated repo info
                        updated_info = GitRepositoryInfo(
                            url=mock_magnet_repo_info.url,
                            name=mock_magnet_repo_info.name,
                            owner=mock_magnet_repo_info.owner,
                            branch=mock_magnet_repo_info.branch,
                            commit_hash="new-commit-hash-after-sync",
                            description=mock_magnet_repo_info.description,
                            file_count=mock_magnet_repo_info.file_count + 2,  # Added files
                            total_size=mock_magnet_repo_info.total_size + 5000  # Added content
                        )
                        mock_update.return_value = updated_info

                        # Start sync
                        sync_response = client.put(
                            f"/api/repositories/{repository_id}/sync",
                            headers={"Authorization": "Bearer test-token"}
                        )

                        assert sync_response.status_code == 200
                        sync_data = sync_response.json()
                        assert "message" in sync_data
                        assert "sync started" in sync_data["message"].lower()

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_magnet_repository_version_history(self, async_client: AsyncClient, mock_user):
        """Test viewing repository version history."""

        repository_id = "magnet-repo-123"

        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_auth.return_value = mock_user

            with patch('src.routes.repositories.select') as mock_select:
                # Mock repository exists
                mock_repository = Mock()
                mock_repository.id = repository_id
                mock_repository.name = "magnet"

                # Mock version history
                mock_versions = []
                commits = [
                    ("v2.1.0", "feat: Add advanced particle modeling"),
                    ("v2.0.5", "fix: Improve fluid dynamics calculations"),
                    ("v2.0.4", "docs: Update API documentation"),
                    ("v2.0.3", "refactor: Optimize physics engine"),
                    ("v2.0.2", "fix: Memory leak in simulation loop")
                ]

                for i, (version, summary) in enumerate(commits):
                    mock_version = Mock()
                    mock_version.id = f"version-{i+1}"
                    mock_version.commit_hash = f"commit-hash-{i+1}"
                    mock_version.branch = "main"
                    mock_version.file_count = 42 + i
                    mock_version.total_size = 256000 + (i * 1000)
                    mock_version.changes_summary = summary
                    mock_version.created_at = f"2024-01-{10+i:02d}T12:00:00Z"
                    mock_versions.append(mock_version)

                def mock_select_func(*args):
                    mock_result = Mock()
                    if "Repository" in str(args):
                        mock_result.scalar_one_or_none.return_value = mock_repository
                    else:  # RepositoryVersion query
                        mock_result.scalars.return_value.all.return_value = mock_versions
                    return mock_result

                mock_select.side_effect = mock_select_func

                with patch('src.routes.repositories.get_async_db') as mock_db:
                    mock_session = AsyncMock()
                    mock_session.execute.side_effect = mock_select_func
                    mock_db.return_value.__anext__ = AsyncMock(return_value=mock_session)

                    versions_response = await async_client.get(
                        f"/api/repositories/{repository_id}/versions",
                        headers={"Authorization": "Bearer test-token"}
                    )

                    assert versions_response.status_code == 200
                    versions_data = versions_response.json()
                    assert len(versions_data) == 5

                    # Check version details
                    latest_version = versions_data[0]
                    assert latest_version["changes_summary"] == "feat: Add advanced particle modeling"
                    assert latest_version["branch"] == "main"
                    assert latest_version["file_count"] == 42

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_magnet_repository_update_checking(self, async_client: AsyncClient, mock_user):
        """Test checking for repository updates."""

        repository_id = "magnet-repo-123"

        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_auth.return_value = mock_user

            with patch('src.routes.repositories.select') as mock_select:
                mock_repository = Mock()
                mock_repository.id = repository_id
                mock_repository.name = "magnet"
                mock_repository.commit_hash = "current-commit-hash"
                mock_repository.last_synced_at = "2024-01-10T12:00:00Z"

                mock_result = Mock()
                mock_result.scalar_one_or_none.return_value = mock_repository

                with patch('src.routes.repositories.get_async_db') as mock_db:
                    mock_session = AsyncMock()
                    mock_session.execute.return_value = mock_result
                    mock_db.return_value.__anext__ = AsyncMock(return_value=mock_session)

                    # Mock repository service check
                    with patch('src.services.repository_service.RepositoryService.check_for_updates') as mock_check:
                        mock_check.return_value = True  # Updates available

                        updates_response = await async_client.post(
                            f"/api/repositories/{repository_id}/check-updates",
                            headers={"Authorization": "Bearer test-token"}
                        )

                        assert updates_response.status_code == 200
                        updates_data = updates_response.json()
                        assert updates_data["repository_id"] == repository_id
                        assert updates_data["has_updates"] is True
                        assert updates_data["current_commit"] == "current-commit-hash"

    @pytest.mark.e2e
    def test_magnet_repository_deletion_workflow(self, client: TestClient, mock_user):
        """Test complete repository deletion workflow."""

        repository_id = "magnet-repo-123"

        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_auth.return_value = mock_user

            with patch('src.routes.repositories.select') as mock_select:
                mock_repository = Mock()
                mock_repository.id = repository_id
                mock_repository.name = "magnet"

                mock_result = Mock()
                mock_result.scalar_one_or_none.return_value = mock_repository

                with patch('src.routes.repositories.get_async_db') as mock_db:
                    mock_session = Mock()
                    mock_session.execute.return_value = mock_result
                    mock_session.commit.return_value = None
                    mock_db.return_value.__anext__ = Mock(return_value=mock_session)

                    # Mock file system deletion
                    with patch('src.services.git_service.GitService.repository_exists') as mock_exists:
                        mock_exists.return_value = True

                        with patch('src.services.git_service.GitService.delete_repository') as mock_delete:
                            mock_delete.return_value = True

                            delete_response = client.delete(
                                f"/api/repositories/{repository_id}",
                                headers={"Authorization": "Bearer test-token"}
                            )

                            assert delete_response.status_code == 200
                            delete_data = delete_response.json()
                            assert "deleted successfully" in delete_data["message"].lower()

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_user_authentication_failure_scenarios(self, async_client: AsyncClient):
        """Test authentication failure scenarios in the user journey."""

        # Test without authentication
        no_auth_response = await async_client.post(
            "/api/repositories/import",
            json={
                "url": self.MAGNET_REPO_URL,
                "name": "Should Fail"
            }
        )

        # Should fail without proper authentication
        assert no_auth_response.status_code in [401, 403, 422]

        # Test with invalid token
        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_auth.side_effect = Exception("Invalid token")

            invalid_auth_response = await async_client.post(
                "/api/repositories/import",
                json={
                    "url": self.MAGNET_REPO_URL,
                    "name": "Should Also Fail"
                },
                headers={"Authorization": "Bearer invalid-token"}
            )

            # Should handle authentication error
            assert invalid_auth_response.status_code in [401, 403, 500]

    @pytest.mark.e2e
    def test_repository_access_control(self, client: TestClient):
        """Test repository access control across different users."""

        repository_id = "magnet-repo-123"

        # User 1 creates repository
        user1 = {"id": "user1", "email": "user1@example.com"}
        # User 2 tries to access it
        user2 = {"id": "user2", "email": "user2@example.com"}

        # Mock User 2 trying to access User 1's repository
        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_auth.return_value = user2

            with patch('src.routes.repositories.select') as mock_select:
                # No repository found for user2
                mock_result = Mock()
                mock_result.scalar_one_or_none.return_value = None

                with patch('src.routes.repositories.get_async_db') as mock_db:
                    mock_session = Mock()
                    mock_session.execute.return_value = mock_result
                    mock_db.return_value.__anext__ = Mock(return_value=mock_session)

                    # Try to access repository files
                    access_response = client.get(
                        f"/api/repositories/{repository_id}/files",
                        headers={"Authorization": "Bearer user2-token"}
                    )

                    # Should deny access
                    assert access_response.status_code == 404
                    assert "not found or access denied" in access_response.json()["detail"].lower()
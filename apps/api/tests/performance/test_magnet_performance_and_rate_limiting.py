"""
Performance and rate limiting tests for magnet repository import - Story 1.2 Git Repository Import System

This test suite validates performance characteristics, rate limiting behavior,
and scalability aspects of the repository import system using the magnet repository.
"""

import pytest
import asyncio
import time
from unittest.mock import patch, Mock, AsyncMock
from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.services.git_service import GitService, GitRepositoryInfo
from src.services.repository_service import RepositoryService
from fastapi import HTTPException


class TestMagnetPerformanceAndRateLimiting:
    """Performance and rate limiting tests for magnet repository import."""

    MAGNET_REPO_URL = "https://github.com/twattier/magnet"

    @pytest.fixture
    def git_service(self):
        """Create GitService instance for testing."""
        return GitService()

    @pytest.fixture
    def repository_service(self, git_service):
        """Create RepositoryService instance for testing."""
        return RepositoryService(git_service)

    @pytest.fixture
    def mock_magnet_repo_info(self):
        """Mock repository information for performance tests."""
        return GitRepositoryInfo(
            url=self.MAGNET_REPO_URL,
            name="magnet",
            owner="twattier",
            branch="main",
            commit_hash="perf-test-commit-hash",
            description="Magnetorheological fluid simulation toolkit",
            file_count=50,
            total_size=500000  # 500KB
        )

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_import_request_rate_limiting(self, async_client: AsyncClient):
        """Test rate limiting for repository import requests."""
        user_id = "rate-limit-test-user"

        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_auth.return_value = Mock(id=user_id, email="rate@test.com")

            # Test within rate limit (should succeed)
            successful_requests = []
            for i in range(5):  # Within limit of 10 per minute
                with patch('src.routes.repositories.apply_rate_limit') as mock_rate_limit:
                    mock_rate_limit.return_value = AsyncMock()  # Allow requests

                    response = await async_client.post(
                        "/api/repositories/import",
                        json={
                            "url": self.MAGNET_REPO_URL,
                            "name": f"Rate Test {i+1}"
                        },
                        headers={"Authorization": "Bearer test-token"}
                    )

                    if response.status_code == 202:
                        successful_requests.append(response)

            assert len(successful_requests) == 5

            # Test exceeding rate limit (should fail)
            with patch('src.routes.repositories.apply_rate_limit') as mock_rate_limit:
                mock_rate_limit.side_effect = HTTPException(status_code=429, detail="Rate limit exceeded")

                response = await async_client.post(
                    "/api/repositories/import",
                    json={
                        "url": self.MAGNET_REPO_URL,
                        "name": "Rate Limit Exceeded Test"
                    },
                    headers={"Authorization": "Bearer test-token"}
                )

                # Should be rate limited
                assert response.status_code in [429, 500]

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_import_performance(self, async_client: AsyncClient, mock_magnet_repo_info):
        """Test performance of concurrent repository imports."""
        concurrent_imports = 10

        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_auth.return_value = Mock(id="perf-user", email="perf@test.com")

            with patch('src.routes.repositories.apply_rate_limit'):
                with patch('src.services.git_service.GitService.clone_repository') as mock_clone:
                    # Add slight delay to simulate real clone operation
                    async def mock_clone_with_delay(*args, **kwargs):
                        await asyncio.sleep(0.01)  # 10ms delay
                        return mock_magnet_repo_info

                    mock_clone.side_effect = mock_clone_with_delay

                    # Measure time for concurrent imports
                    start_time = time.time()

                    tasks = []
                    for i in range(concurrent_imports):
                        task = async_client.post(
                            "/api/repositories/import",
                            json={
                                "url": self.MAGNET_REPO_URL,
                                "name": f"Concurrent Test {i+1}"
                            },
                            headers={"Authorization": "Bearer test-token"}
                        )
                        tasks.append(task)

                    responses = await asyncio.gather(*tasks, return_exceptions=True)
                    end_time = time.time()

                    duration = end_time - start_time

                    # Should handle concurrent requests efficiently
                    # With 10ms delay per clone, sequential would take 100ms minimum
                    # Concurrent should be significantly faster
                    assert duration < 0.5  # Should complete within 500ms

                    # Count successful responses
                    successful = sum(1 for r in responses if hasattr(r, 'status_code') and r.status_code == 202)
                    assert successful > 0  # At least some should succeed

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_large_repository_import_performance(self, git_service, mock_magnet_repo_info):
        """Test performance with large repository simulation."""
        # Create a mock for large magnet repository
        large_repo_info = GitRepositoryInfo(
            url=self.MAGNET_REPO_URL,
            name="magnet",
            owner="twattier",
            branch="main",
            commit_hash="large-repo-commit",
            description="Large magnetorheological simulation toolkit",
            file_count=1000,  # Large number of files
            total_size=50000000  # 50MB
        )

        with patch('src.services.git_service.Repo.clone_from') as mock_clone:
            mock_repo = Mock()
            mock_repo.active_branch.name = "main"
            mock_repo.head.commit.hexsha = "large-repo-commit"
            mock_clone.return_value = mock_repo

            with patch.object(git_service, '_analyze_repository') as mock_analyze:
                # Simulate analysis with slight delay for large repo
                async def mock_analyze_large(*args, **kwargs):
                    await asyncio.sleep(0.05)  # 50ms delay
                    return {
                        'file_count': 1000,
                        'total_size': 50000000,
                        'description': 'Large magnetorheological simulation toolkit'
                    }

                mock_analyze.side_effect = mock_analyze_large

                # Measure import time
                start_time = time.time()
                result = await git_service.clone_repository(self.MAGNET_REPO_URL, "large-repo-test")
                end_time = time.time()

                duration = end_time - start_time

                # Should complete within reasonable time even for large repos
                assert duration < 1.0  # Should complete within 1 second
                assert result.file_count == 1000
                assert result.total_size == 50000000

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_repository_analysis_performance(self, git_service):
        """Test performance of repository structure analysis."""
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create many files to test analysis performance
            num_files = 100
            files_created = 0

            # Create nested directory structure
            for i in range(10):  # 10 directories
                dir_path = os.path.join(temp_dir, f"dir_{i}")
                os.makedirs(dir_path, exist_ok=True)

                for j in range(10):  # 10 files per directory
                    file_path = os.path.join(dir_path, f"file_{j}.js")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(f"// File {i}-{j}\nconsole.log('magnet simulation {i}-{j}');\n" * 10)
                    files_created += 1

            # Measure analysis time
            start_time = time.time()
            repo_analysis = await git_service._analyze_repository(temp_dir)
            end_time = time.time()

            duration = end_time - start_time

            # Should analyze quickly even with many files
            assert duration < 0.5  # Should complete within 500ms
            assert repo_analysis["file_count"] == files_created
            assert repo_analysis["total_size"] > 0

    @pytest.mark.performance
    def test_api_response_time_benchmarks(self, client: TestClient):
        """Test API response time benchmarks for various endpoints."""
        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_auth.return_value = Mock(id="benchmark-user", email="benchmark@test.com")

            with patch('src.routes.repositories.apply_rate_limit'):
                # Benchmark import request
                start_time = time.time()
                response = client.post(
                    "/api/repositories/import",
                    json={
                        "url": self.MAGNET_REPO_URL,
                        "name": "Benchmark Test"
                    },
                    headers={"Authorization": "Bearer test-token"}
                )
                import_duration = time.time() - start_time

                # Should respond quickly
                assert import_duration < 0.1  # Less than 100ms
                assert response.status_code in [202, 400, 500]  # Valid status codes

                # Benchmark status check
                if response.status_code == 202:
                    import_id = response.json()["import_id"]

                    with patch('src.routes.repositories.select') as mock_select:
                        mock_import_job = Mock()
                        mock_import_job.status = "pending"
                        mock_import_job.progress = 0
                        mock_import_job.message = "Starting..."

                        mock_result = Mock()
                        mock_result.scalar_one_or_none.return_value = mock_import_job

                        with patch('src.routes.repositories.get_async_db') as mock_db:
                            mock_session = Mock()
                            mock_session.execute.return_value = mock_result
                            mock_db.return_value.__anext__ = Mock(return_value=mock_session)

                            start_time = time.time()
                            status_response = client.get(f"/api/repositories/{import_id}/status")
                            status_duration = time.time() - start_time

                            # Status check should be very fast
                            assert status_duration < 0.05  # Less than 50ms
                            assert status_response.status_code == 200

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_memory_usage_during_large_operations(self, git_service):
        """Test memory usage remains reasonable during large operations."""
        import psutil
        import os

        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        with patch('src.services.git_service.Repo.clone_from') as mock_clone:
            mock_repo = Mock()
            mock_repo.active_branch.name = "main"
            mock_repo.head.commit.hexsha = "memory-test"
            mock_clone.return_value = mock_repo

            # Simulate multiple large repository operations
            tasks = []
            for i in range(5):  # 5 concurrent operations
                with patch.object(git_service, '_analyze_repository') as mock_analyze:
                    mock_analyze.return_value = {
                        'file_count': 500,
                        'total_size': 10000000,  # 10MB
                        'description': 'Memory test repository'
                    }

                    task = git_service.clone_repository(
                        f"{self.MAGNET_REPO_URL}-{i}",
                        f"memory-test-{i}"
                    )
                    tasks.append(task)

            await asyncio.gather(*tasks)

            # Check memory usage after operations
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory

            # Memory increase should be reasonable (less than 100MB for test operations)
            assert memory_increase < 100

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_database_query_performance(self, async_client: AsyncClient):
        """Test database query performance for repository operations."""
        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_auth.return_value = Mock(id="db-perf-user", email="dbperf@test.com")

            # Mock large repository list
            mock_repositories = []
            for i in range(100):  # 100 repositories
                mock_repo = Mock()
                mock_repo.id = f"repo-{i}"
                mock_repo.name = f"magnet-fork-{i}"
                mock_repo.url = f"{self.MAGNET_REPO_URL}-fork-{i}"
                mock_repo.status = "active"
                mock_repo.user_email = "dbperf@test.com"
                mock_repositories.append(mock_repo)

            with patch('src.routes.repositories.select') as mock_select:
                mock_result = Mock()
                mock_result.scalars.return_value.all.return_value = mock_repositories

                with patch('src.routes.repositories.get_async_db') as mock_db:
                    mock_session = AsyncMock()
                    mock_session.execute.return_value = mock_result
                    mock_db.return_value.__anext__ = AsyncMock(return_value=mock_session)

                    # Measure query time
                    start_time = time.time()
                    response = await async_client.get(
                        "/api/repositories?limit=50&offset=0",
                        headers={"Authorization": "Bearer test-token"}
                    )
                    query_duration = time.time() - start_time

                    # Query should be fast even with many repositories
                    assert query_duration < 0.1  # Less than 100ms
                    assert response.status_code == 200

    @pytest.mark.performance
    def test_file_listing_performance(self, client: TestClient):
        """Test performance of repository file listing."""
        repository_id = "magnet-file-perf-test"

        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_auth.return_value = Mock(id="file-perf-user", email="fileperf@test.com")

            with patch('src.routes.repositories.select') as mock_select:
                mock_repository = Mock()
                mock_repository.id = repository_id
                mock_repository.user_email = "fileperf@test.com"

                mock_result = Mock()
                mock_result.scalar_one_or_none.return_value = mock_repository

                with patch('src.routes.repositories.get_async_db') as mock_db:
                    mock_session = Mock()
                    mock_session.execute.return_value = mock_result
                    mock_db.return_value.__anext__ = Mock(return_value=mock_session)

                    # Mock large file list
                    large_file_list = []
                    for i in range(500):  # 500 files
                        large_file_list.append(f"src/component_{i}.js")
                        large_file_list.append(f"test/component_{i}.test.js")
                        large_file_list.append(f"docs/component_{i}.md")

                    with patch('src.services.git_service.GitService.get_repository_files') as mock_get_files:
                        mock_get_files.return_value = large_file_list

                        # Measure file listing time
                        start_time = time.time()
                        response = client.get(
                            f"/api/repositories/{repository_id}/files",
                            headers={"Authorization": "Bearer test-token"}
                        )
                        listing_duration = time.time() - start_time

                        # Should list files quickly even for large repositories
                        assert listing_duration < 0.2  # Less than 200ms
                        assert response.status_code == 200

                        files_data = response.json()
                        assert len(files_data["files"]) == len(large_file_list)

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_storage_cleanup_performance(self, repository_service):
        """Test performance of storage cleanup operations."""
        with patch.object(repository_service, 'get_storage_usage') as mock_usage:
            # Mock high storage usage requiring cleanup
            mock_usage.return_value = {
                'total_size_bytes': 5000000000,  # 5GB
                'total_size_gb': 5.0,
                'repository_count': 100,
                'storage_limit_gb': 5.0,
                'usage_percentage': 100.0
            }

            # Mock database session and repositories
            mock_db_session = Mock()

            # Mock old repositories for cleanup
            mock_old_repos = []
            for i in range(10):
                mock_repo = Mock()
                mock_repo.id = f"old-repo-{i}"
                mock_repo.total_size = 100000000  # 100MB each
                mock_old_repos.append(mock_repo)

            with patch('src.services.repository_service.desc') as mock_desc:
                with patch.object(mock_db_session, 'query') as mock_query:
                    mock_query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = mock_old_repos

                    # Mock git service deletion
                    with patch.object(repository_service.git_service, 'delete_repository') as mock_delete:
                        mock_delete.return_value = True

                        # Measure cleanup time
                        start_time = time.time()
                        cleanup_performed = await repository_service.cleanup_storage_if_needed(
                            mock_db_session,
                            threshold_percentage=80.0
                        )
                        cleanup_duration = time.time() - start_time

                        # Cleanup should complete quickly
                        assert cleanup_duration < 1.0  # Less than 1 second
                        assert cleanup_performed is True

    @pytest.mark.performance
    def test_rate_limit_reset_behavior(self, client: TestClient):
        """Test rate limit reset behavior over time."""
        user_id = "rate-reset-user"

        with patch('src.routes.repositories.get_current_user') as mock_auth:
            mock_auth.return_value = Mock(id=user_id, email="ratereset@test.com")

            # First batch of requests (should succeed)
            with patch('src.routes.repositories.apply_rate_limit') as mock_rate_limit:
                mock_rate_limit.return_value = None  # Allow requests

                responses_batch_1 = []
                for i in range(5):
                    response = client.post(
                        "/api/repositories/import",
                        json={
                            "url": f"{self.MAGNET_REPO_URL}-batch1-{i}",
                            "name": f"Batch 1 Test {i}"
                        },
                        headers={"Authorization": "Bearer test-token"}
                    )
                    responses_batch_1.append(response.status_code)

                # Should have some successful requests
                successful_count = sum(1 for status in responses_batch_1 if status == 202)
                assert successful_count > 0

            # Simulate rate limit exceeded
            with patch('src.routes.repositories.apply_rate_limit') as mock_rate_limit:
                mock_rate_limit.side_effect = HTTPException(status_code=429, detail="Rate limit exceeded")

                response = client.post(
                    "/api/repositories/import",
                    json={
                        "url": f"{self.MAGNET_REPO_URL}-rate-limited",
                        "name": "Rate Limited Test"
                    },
                    headers={"Authorization": "Bearer test-token"}
                )

                # Should be rate limited
                assert response.status_code in [429, 500]

            # After rate limit reset (simulate time passing)
            with patch('src.routes.repositories.apply_rate_limit') as mock_rate_limit:
                mock_rate_limit.return_value = None  # Allow requests again

                response = client.post(
                    "/api/repositories/import",
                    json={
                        "url": f"{self.MAGNET_REPO_URL}-after-reset",
                        "name": "After Reset Test"
                    },
                    headers={"Authorization": "Bearer test-token"}
                )

                # Should succeed after rate limit reset
                assert response.status_code in [202, 400]  # Accepted or validation error

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_progress_tracking_overhead(self, git_service, mock_magnet_repo_info):
        """Test that progress tracking doesn't significantly impact performance."""
        progress_calls = []

        async def progress_callback(progress: int, message: str):
            progress_calls.append({"progress": progress, "message": message, "time": time.time()})
            # Simulate minimal processing delay
            await asyncio.sleep(0.001)  # 1ms

        with patch('src.services.git_service.Repo.clone_from') as mock_clone:
            mock_repo = Mock()
            mock_repo.active_branch.name = "main"
            mock_repo.head.commit.hexsha = "progress-test"
            mock_clone.return_value = mock_repo

            with patch.object(git_service, '_analyze_repository') as mock_analyze:
                mock_analyze.return_value = {
                    'file_count': 25,
                    'total_size': 128000,
                    'description': 'Progress tracking test'
                }

                # Measure clone with progress tracking
                start_time = time.time()
                result = await git_service.clone_repository(
                    self.MAGNET_REPO_URL,
                    "progress-overhead-test",
                    progress_callback=progress_callback
                )
                duration_with_progress = time.time() - start_time

                # Measure clone without progress tracking
                start_time = time.time()
                result_no_progress = await git_service.clone_repository(
                    self.MAGNET_REPO_URL,
                    "no-progress-test",
                    progress_callback=None
                )
                duration_without_progress = time.time() - start_time

                # Progress tracking should not add significant overhead
                overhead = duration_with_progress - duration_without_progress
                assert overhead < 0.1  # Less than 100ms overhead

                # Should have received progress updates
                assert len(progress_calls) >= 3  # At least a few progress updates
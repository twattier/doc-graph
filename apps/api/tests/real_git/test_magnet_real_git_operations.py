"""
Real Git operations tests using the actual magnet repository - Story 1.2 Git Repository Import System

These tests perform actual Git operations against the real magnet repository.
They are marked as @real_git and should be run separately from unit tests
to validate that the import system works with actual Git repositories.

NOTE: These tests require internet connectivity and access to GitHub.
"""

import pytest
import tempfile
import os
import shutil
from pathlib import Path

from src.services.git_service import GitService, GitOperationError


class TestMagnetRealGitOperations:
    """Real Git operations tests against the actual magnet repository."""

    MAGNET_REPO_URL = "https://github.com/twattier/magnet"
    MAGNET_REPO_URL_GIT = "https://github.com/twattier/magnet.git"

    @pytest.fixture
    def git_service(self):
        """Create GitService instance for testing."""
        return GitService()

    @pytest.fixture
    def temp_storage_path(self):
        """Create temporary storage path for real Git operations."""
        temp_dir = tempfile.mkdtemp(prefix="magnet_real_git_")
        yield temp_dir
        # Cleanup after test
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.mark.real_git
    @pytest.mark.slow
    def test_real_magnet_repository_url_validation(self, git_service):
        """Test URL validation against the actual magnet repository."""
        # Test both URL formats
        assert git_service.validate_repository_url(self.MAGNET_REPO_URL) is True
        assert git_service.validate_repository_url(self.MAGNET_REPO_URL_GIT) is True

        # Test repository info parsing
        repo_info = git_service._parse_repository_info(self.MAGNET_REPO_URL)
        assert repo_info["owner"] == "twattier"
        assert repo_info["name"] == "magnet"
        assert repo_info["host"] == "github.com"

    @pytest.mark.real_git
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_real_magnet_repository_clone(self, git_service, temp_storage_path):
        """Test actual cloning of the magnet repository."""
        repo_id = "real_magnet_test"

        # Override the storage path for this test
        original_storage_path = git_service.base_storage_path
        git_service.base_storage_path = temp_storage_path

        try:
            # Perform actual clone operation
            result = await git_service.clone_repository(self.MAGNET_REPO_URL, repo_id)

            # Validate clone results
            assert result.name == "magnet"
            assert result.owner == "twattier"
            assert result.url == self.MAGNET_REPO_URL
            assert result.branch in ["main", "master"]  # Could be either
            assert len(result.commit_hash) == 40  # SHA-1 hash length
            assert result.file_count > 0
            assert result.total_size > 0

            # Verify repository directory exists
            repo_storage_path = git_service.get_repository_storage_path(repo_id)
            assert os.path.exists(repo_storage_path)

            # Verify some expected files exist
            expected_files = ["README.md", "package.json"]
            for expected_file in expected_files:
                file_path = os.path.join(repo_storage_path, expected_file)
                assert os.path.exists(file_path), f"Expected file {expected_file} not found"

        finally:
            # Restore original storage path
            git_service.base_storage_path = original_storage_path

    @pytest.mark.real_git
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_real_magnet_repository_analysis(self, git_service, temp_storage_path):
        """Test analysis of the actual cloned magnet repository."""
        repo_id = "real_magnet_analysis"

        # Override the storage path for this test
        original_storage_path = git_service.base_storage_path
        git_service.base_storage_path = temp_storage_path

        try:
            # Clone the repository
            result = await git_service.clone_repository(self.MAGNET_REPO_URL, repo_id)
            repo_storage_path = git_service.get_repository_storage_path(repo_id)

            # Perform detailed analysis
            repo_analysis = await git_service._analyze_repository(repo_storage_path)

            # Validate analysis results
            assert repo_analysis["file_count"] > 5  # Should have multiple files
            assert repo_analysis["total_size"] > 1000  # Should have substantial content

            # Description should be extracted from README
            if repo_analysis["description"]:
                description = repo_analysis["description"].lower()
                # Should contain relevant keywords from magnet project
                relevant_keywords = ["magnet", "simulation", "fluid", "physics"]
                has_relevant_keyword = any(keyword in description for keyword in relevant_keywords)
                assert has_relevant_keyword, f"Description doesn't contain expected keywords: {description}"

            # Verify file structure analysis
            files = git_service.get_repository_files(repo_id)
            assert len(files) == repo_analysis["file_count"]

            # Check for common JavaScript project files
            js_extensions = [".js", ".json", ".md"]
            js_files = [f for f in files if any(f.endswith(ext) for ext in js_extensions)]
            assert len(js_files) > 0, "No JavaScript/common files found"

        finally:
            git_service.base_storage_path = original_storage_path

    @pytest.mark.real_git
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_real_magnet_repository_file_listing(self, git_service, temp_storage_path):
        """Test file listing functionality with the actual magnet repository."""
        repo_id = "real_magnet_files"

        original_storage_path = git_service.base_storage_path
        git_service.base_storage_path = temp_storage_path

        try:
            # Clone repository
            await git_service.clone_repository(self.MAGNET_REPO_URL, repo_id)

            # Get complete file listing
            all_files = git_service.get_repository_files(repo_id)

            # Validate file listing
            assert len(all_files) > 0
            assert "README.md" in all_files  # Should have README

            # Check for expected project structure
            # Look for common files that JavaScript projects typically have
            common_files = ["package.json", "README.md"]
            found_common_files = [f for f in all_files if f in common_files]
            assert len(found_common_files) > 0, f"No common project files found in {all_files}"

            # Verify no .git files are included
            git_files = [f for f in all_files if ".git/" in f or f.startswith(".git")]
            assert len(git_files) == 0, f"Git files found in listing: {git_files}"

            # Test directory-specific listing if subdirectories exist
            src_files = [f for f in all_files if f.startswith("src/")]
            if src_files:
                # Test getting files from src directory
                src_only_files = git_service.get_repository_files(repo_id, "src")
                # All returned files should be from src directory
                for src_file in src_only_files:
                    assert src_file.startswith("src/"), f"Non-src file in src listing: {src_file}"

        finally:
            git_service.base_storage_path = original_storage_path

    @pytest.mark.real_git
    @pytest.mark.slow
    def test_real_magnet_repository_size_accuracy(self, git_service, temp_storage_path):
        """Test that repository size calculations are accurate for the real magnet repository."""
        repo_id = "real_magnet_size"

        original_storage_path = git_service.base_storage_path
        git_service.base_storage_path = temp_storage_path

        try:
            import asyncio

            # Clone repository
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                git_service.clone_repository(self.MAGNET_REPO_URL, repo_id)
            )

            # Get repository storage path
            repo_storage_path = git_service.get_repository_storage_path(repo_id)

            # Calculate size using our method
            file_count, total_size = git_service.analyze_repository_structure(repo_storage_path)

            # Verify against clone result
            assert file_count == result.file_count
            assert total_size == result.total_size

            # Manual verification - calculate expected size
            manual_total_size = 0
            manual_file_count = 0

            for root, dirs, files in os.walk(repo_storage_path):
                # Skip .git directory
                if '.git' in dirs:
                    dirs.remove('.git')

                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        manual_total_size += os.path.getsize(file_path)
                        manual_file_count += 1
                    except (OSError, IOError):
                        continue

            # Our calculations should match manual calculation
            assert file_count == manual_file_count
            assert total_size == manual_total_size

        finally:
            git_service.base_storage_path = original_storage_path

    @pytest.mark.real_git
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_real_magnet_repository_update_check(self, git_service, temp_storage_path):
        """Test update checking functionality with the real magnet repository."""
        repo_id = "real_magnet_update"

        original_storage_path = git_service.base_storage_path
        git_service.base_storage_path = temp_storage_path

        try:
            # Clone repository
            initial_result = await git_service.clone_repository(self.MAGNET_REPO_URL, repo_id)
            initial_commit = initial_result.commit_hash

            # Verify repository exists
            assert git_service.repository_exists(repo_id)

            # Test repository update (should be no-op if no changes)
            update_result = await git_service.update_repository(repo_id)

            # Update result should have same or newer commit
            assert update_result.name == "magnet"
            assert update_result.owner == "twattier"
            assert len(update_result.commit_hash) == 40

            # Repository should still exist after update
            assert git_service.repository_exists(repo_id)

        finally:
            git_service.base_storage_path = original_storage_path

    @pytest.mark.real_git
    @pytest.mark.slow
    def test_real_magnet_repository_deletion(self, git_service, temp_storage_path):
        """Test repository deletion with the real magnet repository."""
        repo_id = "real_magnet_delete"

        original_storage_path = git_service.base_storage_path
        git_service.base_storage_path = temp_storage_path

        try:
            import asyncio

            # Clone repository
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                git_service.clone_repository(self.MAGNET_REPO_URL, repo_id)
            )

            # Verify repository exists
            assert git_service.repository_exists(repo_id)
            repo_path = git_service.get_repository_storage_path(repo_id)
            assert os.path.exists(repo_path)

            # Delete repository
            deletion_success = git_service.delete_repository(repo_id)

            # Verify deletion
            assert deletion_success is True
            assert not git_service.repository_exists(repo_id)
            assert not os.path.exists(repo_path)

        finally:
            git_service.base_storage_path = original_storage_path

    @pytest.mark.real_git
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_real_magnet_repository_progress_tracking(self, git_service, temp_storage_path):
        """Test progress tracking during actual repository clone."""
        repo_id = "real_magnet_progress"
        progress_updates = []

        async def progress_callback(progress: int, message: str):
            progress_updates.append({
                "progress": progress,
                "message": message
            })

        original_storage_path = git_service.base_storage_path
        git_service.base_storage_path = temp_storage_path

        try:
            # Clone with progress tracking
            result = await git_service.clone_repository(
                self.MAGNET_REPO_URL,
                repo_id,
                progress_callback=progress_callback
            )

            # Verify clone succeeded
            assert result.name == "magnet"

            # Verify progress updates were received
            assert len(progress_updates) > 0

            # Check progress progression
            progresses = [update["progress"] for update in progress_updates]
            assert progresses[0] <= progresses[-1]  # Should progress forward
            assert progresses[-1] == 100  # Should complete at 100%

            # Check for expected progress messages
            messages = [update["message"].lower() for update in progress_updates]
            expected_keywords = ["clone", "repository", "success"]
            for keyword in expected_keywords:
                has_keyword = any(keyword in msg for msg in messages)
                assert has_keyword, f"Expected keyword '{keyword}' not found in progress messages"

        finally:
            git_service.base_storage_path = original_storage_path

    @pytest.mark.real_git
    @pytest.mark.slow
    def test_real_magnet_repository_error_handling(self, git_service, temp_storage_path):
        """Test error handling with invalid URLs and real Git failures."""
        original_storage_path = git_service.base_storage_path
        git_service.base_storage_path = temp_storage_path

        try:
            import asyncio

            # Test non-existent repository
            fake_magnet_url = "https://github.com/twattier/magnet-nonexistent"

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            with pytest.raises(GitOperationError):
                loop.run_until_complete(
                    git_service.clone_repository(fake_magnet_url, "fake-magnet")
                )

            # Test invalid URL format
            invalid_url = "not-a-valid-url-at-all"

            with pytest.raises(GitOperationError) as exc_info:
                loop.run_until_complete(
                    git_service.clone_repository(invalid_url, "invalid-url")
                )

            assert "Invalid repository URL" in str(exc_info.value)

        finally:
            git_service.base_storage_path = original_storage_path

    @pytest.mark.real_git
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_real_magnet_commit_hash_and_branch_info(self, git_service, temp_storage_path):
        """Test that commit hash and branch information is accurately extracted from real repository."""
        repo_id = "real_magnet_commit_info"

        original_storage_path = git_service.base_storage_path
        git_service.base_storage_path = temp_storage_path

        try:
            # Clone repository
            result = await git_service.clone_repository(self.MAGNET_REPO_URL, repo_id)

            # Validate commit hash format (SHA-1)
            assert len(result.commit_hash) == 40
            assert all(c in '0123456789abcdef' for c in result.commit_hash.lower())

            # Validate branch name
            assert result.branch in ["main", "master", "develop"]  # Common branch names

            # Verify we can access the repository to validate the commit
            repo_path = git_service.get_repository_storage_path(repo_id)
            git_dir = os.path.join(repo_path, ".git")
            assert os.path.exists(git_dir), "Git directory not found in cloned repository"

            # Check HEAD file exists (indicates successful clone)
            head_file = os.path.join(git_dir, "HEAD")
            assert os.path.exists(head_file), "HEAD file not found in .git directory"

        finally:
            git_service.base_storage_path = original_storage_path
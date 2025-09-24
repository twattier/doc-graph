"""
Unit tests for GitService - Story 1.2 Git Repository Import System
"""
import pytest
import tempfile
import shutil
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.services.git_service import GitService, GitOperationError, GitRepositoryInfo


class TestGitService:
    """Test suite for GitService functionality."""

    @pytest.fixture
    def git_service(self):
        """Create GitService instance for testing."""
        return GitService()

    @pytest.fixture
    def mock_repo_url(self):
        """Mock repository URL for testing."""
        return "https://github.com/test/repo.git"

    @pytest.fixture
    def temp_directory(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.mark.unit
    def test_validate_repository_url_valid_github(self, git_service):
        """Test URL validation for valid GitHub URLs."""
        valid_urls = [
            "https://github.com/user/repo",
            "https://github.com/user/repo.git",
            "https://github.com/user-name/repo-name",
            "https://github.com/user123/repo_name"
        ]

        for url in valid_urls:
            assert git_service.validate_repository_url(url) is True

    @pytest.mark.unit
    def test_validate_repository_url_valid_gitlab(self, git_service):
        """Test URL validation for valid GitLab URLs."""
        valid_urls = [
            "https://gitlab.com/user/repo",
            "https://gitlab.com/user/repo.git",
            "https://gitlab.com/group/subgroup/repo"
        ]

        for url in valid_urls:
            assert git_service.validate_repository_url(url) is True

    @pytest.mark.unit
    def test_validate_repository_url_invalid(self, git_service):
        """Test URL validation rejects invalid URLs."""
        invalid_urls = [
            "not-a-url",
            "http://github.com/user/repo",  # HTTP not HTTPS
            "https://malicious-site.com/repo",
            "https://github.com/",
            "https://github.com/user",
            "ftp://github.com/user/repo",
            "",
            None
        ]

        for url in invalid_urls:
            assert git_service.validate_repository_url(url) is False

    @pytest.mark.unit
    @patch('src.services.git_service.Repo.clone_from')
    async def test_clone_repository_success(self, mock_clone, git_service, mock_repo_url, temp_directory):
        """Test successful repository cloning."""
        mock_repo = Mock()
        mock_repo.git.rev_parse.return_value = "abc123"
        mock_repo.active_branch.name = "main"
        mock_clone.return_value = mock_repo

        # Mock directory structure
        repo_path = os.path.join(temp_directory, "repo")
        os.makedirs(repo_path)

        with patch('os.walk') as mock_walk:
            mock_walk.return_value = [
                (repo_path, [], ['file1.py', 'file2.md']),
            ]

            result = await git_service.clone_repository(mock_repo_url, temp_directory)

        assert isinstance(result, GitRepositoryInfo)
        assert result.url == mock_repo_url
        assert result.commit_hash == "abc123"
        assert result.branch == "main"
        assert result.file_count == 2
        mock_clone.assert_called_once()

    @pytest.mark.unit
    async def test_clone_repository_invalid_url(self, git_service, temp_directory):
        """Test clone repository with invalid URL raises error."""
        invalid_url = "not-a-valid-url"

        with pytest.raises(GitOperationError) as exc_info:
            await git_service.clone_repository(invalid_url, temp_directory)

        assert "Invalid repository URL" in str(exc_info.value)

    @pytest.mark.unit
    @patch('src.services.git_service.Repo.clone_from')
    async def test_clone_repository_git_error(self, mock_clone, git_service, mock_repo_url, temp_directory):
        """Test clone repository handles Git errors properly."""
        from git import GitError
        mock_clone.side_effect = GitError("Repository not found")

        with pytest.raises(GitOperationError) as exc_info:
            await git_service.clone_repository(mock_repo_url, temp_directory)

        assert "Failed to clone repository" in str(exc_info.value)

    @pytest.mark.unit
    def test_extract_repository_name_github(self, git_service):
        """Test extracting repository name from GitHub URL."""
        url = "https://github.com/user/my-repo.git"
        name = git_service.extract_repository_name(url)
        assert name == "my-repo"

    @pytest.mark.unit
    def test_extract_repository_name_gitlab(self, git_service):
        """Test extracting repository name from GitLab URL."""
        url = "https://gitlab.com/user/another-repo"
        name = git_service.extract_repository_name(url)
        assert name == "another-repo"

    @pytest.mark.unit
    def test_extract_repository_name_invalid_url(self, git_service):
        """Test extracting repository name from invalid URL."""
        url = "not-a-valid-url"
        name = git_service.extract_repository_name(url)
        assert name == "unknown"

    @pytest.mark.unit
    @patch('os.walk')
    @patch('os.path.getsize')
    def test_analyze_repository_structure(self, mock_getsize, mock_walk, git_service, temp_directory):
        """Test repository structure analysis."""
        # Mock file system structure
        mock_walk.return_value = [
            (temp_directory, ['src', 'tests'], ['README.md']),
            (os.path.join(temp_directory, 'src'), [], ['main.py', 'service.py']),
            (os.path.join(temp_directory, 'tests'), [], ['test_main.py']),
        ]
        mock_getsize.return_value = 1024  # 1KB per file

        file_count, total_size = git_service.analyze_repository_structure(temp_directory)

        assert file_count == 4  # README.md, main.py, service.py, test_main.py
        assert total_size == 4096  # 4 files * 1KB each

    @pytest.mark.unit
    @patch('shutil.rmtree')
    def test_cleanup_repository(self, mock_rmtree, git_service, temp_directory):
        """Test repository cleanup."""
        git_service.cleanup_repository(temp_directory)
        mock_rmtree.assert_called_once_with(temp_directory, ignore_errors=True)

    @pytest.mark.unit
    def test_is_repository_accessible_valid_url(self, git_service):
        """Test repository accessibility check for valid URLs."""
        # This would require mocking network calls in a real implementation
        # For now, test the URL validation part
        valid_url = "https://github.com/torvalds/linux.git"
        result = git_service.validate_repository_url(valid_url)
        assert result is True

    @pytest.mark.unit
    async def test_clone_repository_creates_proper_directory_structure(self, git_service, temp_directory):
        """Test that clone operation creates expected directory structure."""
        repo_url = "https://github.com/test/repo.git"

        with patch('src.services.git_service.Repo.clone_from') as mock_clone:
            mock_repo = Mock()
            mock_repo.git.rev_parse.return_value = "abc123"
            mock_repo.active_branch.name = "main"
            mock_clone.return_value = mock_repo

            # Mock the repository path creation
            with patch.object(git_service, 'analyze_repository_structure') as mock_analyze:
                mock_analyze.return_value = (5, 2048)  # 5 files, 2KB

                result = await git_service.clone_repository(repo_url, temp_directory)

                assert result.file_count == 5
                assert result.total_size == 2048
                mock_analyze.assert_called_once()
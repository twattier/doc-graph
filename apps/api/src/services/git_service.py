"""
Git repository operations service for cloning and managing repositories.
"""

import os
import shutil
import asyncio
from typing import Optional, Dict, Any, Callable, List, Tuple
from urllib.parse import urlparse
import logging

from git import Repo, GitError
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class GitRepositoryInfo(BaseModel):
    """Information about a Git repository."""
    url: str
    name: str
    owner: str
    branch: str
    commit_hash: str
    description: Optional[str] = None
    file_count: int = 0
    total_size: int = 0


class GitOperationError(Exception):
    """Custom exception for Git operation errors."""
    pass


class GitService:
    """Service for Git repository operations."""

    def __init__(self, base_storage_path: str = "/app/data/repositories"):
        """Initialize the Git service with a base storage path."""
        self.base_storage_path = base_storage_path
        self._ensure_storage_directory()

    def _ensure_storage_directory(self) -> None:
        """Ensure the storage directory exists."""
        os.makedirs(self.base_storage_path, exist_ok=True)

    def validate_repository_url(self, url: str) -> bool:
        """
        Validate if the provided URL is a valid Git repository URL.

        Args:
            url: The repository URL to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not url or not isinstance(url, str) or not url.strip():
            return False

        url = url.strip()

        # Check for HTTPS patterns with proper repository structure
        https_patterns = [
            'https://github.com/',
            'https://gitlab.com/',
            'https://bitbucket.org/',
        ]

        # Check for SSH patterns with proper repository structure
        ssh_patterns = [
            'git@github.com:',
            'git@gitlab.com:',
            'git@bitbucket.org:',
        ]

        # Check if URL matches one of the valid hosting patterns
        matches_pattern = any(url.startswith(pattern) for pattern in https_patterns + ssh_patterns)

        if not matches_pattern:
            return False

        # For HTTPS URLs, validate the structure
        if url.startswith('https://'):
            try:
                parsed = urlparse(url)
                path_parts = parsed.path.strip('/').split('/')

                # Must have at least owner/repo structure
                if len(path_parts) < 2:
                    return False

                # Check that owner and repo names are not empty
                owner, repo = path_parts[0], path_parts[1]
                if not owner or not repo:
                    return False

                # Reject URLs with tree/branch paths (e.g., /tree/main, /blob/master)
                # Check if any part contains branch/tree indicators
                for part in path_parts:
                    if part in ['tree', 'blob', 'commit', 'releases', 'tags']:
                        return False

                # Must have at least 2 parts and all parts must be non-empty
                # Allow group/subgroup/repo structures for GitLab
                if any(part == '' for part in path_parts):
                    return False

                return True
            except Exception:
                return False

        # For SSH URLs, validate the structure
        elif any(url.startswith(pattern) for pattern in ssh_patterns):
            try:
                # Extract the part after the colon
                if ':' not in url:
                    return False

                _, path_part = url.split(':', 1)
                path_parts = path_part.strip('/').split('/')

                # Must have at least owner/repo structure
                if len(path_parts) < 2:
                    return False

                # Check that owner and repo names are not empty
                owner, repo = path_parts[0], path_parts[1]
                if not owner or not repo:
                    return False

                return True
            except Exception:
                return False

        return False

    def _parse_repository_info(self, url: str) -> Dict[str, str]:
        """
        Parse repository information from URL.

        Args:
            url: Repository URL

        Returns:
            Dict containing owner, name, and other info
        """
        url = url.strip()

        # Handle SSH URLs
        if url.startswith('git@'):
            # Convert git@github.com:owner/repo.git to https format for parsing
            if ':' in url:
                host_part, path_part = url.split(':', 1)
                host = host_part.replace('git@', '')
                url = f"https://{host}/{path_part}"

        # Remove .git suffix if present
        if url.endswith('.git'):
            url = url[:-4]

        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')

        if len(path_parts) < 2:
            raise GitOperationError(f"Invalid repository URL format: {url}")

        return {
            'host': parsed.netloc,
            'owner': path_parts[0],
            'name': path_parts[1],
            'full_path': '/'.join(path_parts)
        }

    def get_repository_storage_path(self, repository_id: str) -> str:
        """Get the storage path for a repository."""
        return os.path.join(self.base_storage_path, repository_id)

    async def clone_repository(
        self,
        url: str,
        repository_id: str,
        progress_callback: Optional[Callable] = None
    ) -> GitRepositoryInfo:
        """
        Clone a Git repository asynchronously.

        Args:
            url: Repository URL to clone
            repository_id: Unique identifier for storage
            progress_callback: Optional callback for progress updates

        Returns:
            GitRepositoryInfo: Information about the cloned repository

        Raises:
            GitOperationError: If cloning fails
        """
        if not self.validate_repository_url(url):
            raise GitOperationError(f"Invalid repository URL: {url}")

        try:
            repo_info = self._parse_repository_info(url)
            storage_path = self.get_repository_storage_path(repository_id)

            # Remove existing directory if it exists
            if os.path.exists(storage_path):
                shutil.rmtree(storage_path)

            if progress_callback:
                await progress_callback(10, "Initializing clone operation...")

            # Clone repository in a separate thread to avoid blocking
            def clone_repo():
                try:
                    return Repo.clone_from(url, storage_path, depth=1)
                except GitError as e:
                    raise GitOperationError(f"Failed to clone repository: {str(e)}")

            if progress_callback:
                await progress_callback(30, "Cloning repository...")

            # Run the clone operation in a thread pool
            loop = asyncio.get_event_loop()
            repo = await loop.run_in_executor(None, clone_repo)

            if progress_callback:
                await progress_callback(70, "Analyzing repository structure...")

            # Analyze the cloned repository
            repo_analysis = await self._analyze_repository(storage_path)

            if progress_callback:
                await progress_callback(90, "Finalizing import...")

            # Create repository info
            git_info = GitRepositoryInfo(
                url=url,
                name=repo_info['name'],
                owner=repo_info['owner'],
                branch=repo.active_branch.name if repo.active_branch else 'main',
                commit_hash=str(repo.head.commit.hexsha),
                description=repo_analysis.get('description'),
                file_count=repo_analysis['file_count'],
                total_size=repo_analysis['total_size']
            )

            if progress_callback:
                await progress_callback(100, "Repository cloned successfully!")

            logger.info(f"Successfully cloned repository {url} to {storage_path}")
            return git_info

        except GitError as e:
            error_msg = f"Git operation failed: {str(e)}"
            logger.error(error_msg)
            raise GitOperationError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error during clone: {str(e)}"
            logger.error(error_msg)
            raise GitOperationError(error_msg)

    async def _analyze_repository(self, repo_path: str) -> Dict[str, Any]:
        """
        Analyze a cloned repository to extract metadata.

        Args:
            repo_path: Path to the cloned repository

        Returns:
            Dict containing repository analysis results
        """
        def analyze():
            file_count = 0
            total_size = 0

            for root, dirs, files in os.walk(repo_path):
                # Skip .git directory
                if '.git' in dirs:
                    dirs.remove('.git')

                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(file_path)
                        file_count += 1
                    except (OSError, IOError):
                        # Skip files we can't access
                        continue

            # Look for common description files
            description = None
            description_files = ['README.md', 'README.txt', 'readme.md']

            for desc_file in description_files:
                desc_path = os.path.join(repo_path, desc_file)
                if os.path.exists(desc_path):
                    try:
                        with open(desc_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Take first paragraph as description
                            lines = content.split('\n')
                            for line in lines:
                                line = line.strip()
                                if line and not line.startswith('#'):
                                    description = line[:200]  # Limit to 200 chars
                                    break
                    except (OSError, IOError, UnicodeDecodeError):
                        continue
                    break

            return {
                'file_count': file_count,
                'total_size': total_size,
                'description': description
            }

        # Run analysis in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, analyze)

    async def update_repository(
        self,
        repository_id: str,
        progress_callback: Optional[Callable] = None
    ) -> GitRepositoryInfo:
        """
        Update an existing repository by pulling latest changes.

        Args:
            repository_id: Repository identifier
            progress_callback: Optional callback for progress updates

        Returns:
            GitRepositoryInfo: Updated repository information

        Raises:
            GitOperationError: If update fails
        """
        storage_path = self.get_repository_storage_path(repository_id)

        if not os.path.exists(storage_path):
            raise GitOperationError(f"Repository not found: {repository_id}")

        try:
            if progress_callback:
                await progress_callback(20, "Opening repository...")

            def pull_changes():
                repo = Repo(storage_path)
                origin = repo.remotes.origin
                return origin.pull(), repo

            if progress_callback:
                await progress_callback(50, "Pulling latest changes...")

            # Pull changes in thread pool
            loop = asyncio.get_event_loop()
            pull_result, repo = await loop.run_in_executor(None, pull_changes)

            if progress_callback:
                await progress_callback(80, "Analyzing updated repository...")

            # Re-analyze the repository
            repo_analysis = await self._analyze_repository(storage_path)

            # Parse URL info
            url = repo.remotes.origin.url
            repo_info = self._parse_repository_info(url)

            git_info = GitRepositoryInfo(
                url=url,
                name=repo_info['name'],
                owner=repo_info['owner'],
                branch=repo.active_branch.name if repo.active_branch else 'main',
                commit_hash=str(repo.head.commit.hexsha),
                description=repo_analysis.get('description'),
                file_count=repo_analysis['file_count'],
                total_size=repo_analysis['total_size']
            )

            if progress_callback:
                await progress_callback(100, "Repository updated successfully!")

            logger.info(f"Successfully updated repository {repository_id}")
            return git_info

        except GitError as e:
            error_msg = f"Git update failed: {str(e)}"
            logger.error(error_msg)
            raise GitOperationError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error during update: {str(e)}"
            logger.error(error_msg)
            raise GitOperationError(error_msg)

    def delete_repository(self, repository_id: str) -> bool:
        """
        Delete a repository from storage.

        Args:
            repository_id: Repository identifier

        Returns:
            bool: True if deleted successfully, False if not found
        """
        storage_path = self.get_repository_storage_path(repository_id)

        if not os.path.exists(storage_path):
            return False

        try:
            shutil.rmtree(storage_path)
            logger.info(f"Deleted repository storage: {storage_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete repository {repository_id}: {str(e)}")
            raise GitOperationError(f"Failed to delete repository: {str(e)}")

    def repository_exists(self, repository_id: str) -> bool:
        """Check if a repository exists in storage."""
        storage_path = self.get_repository_storage_path(repository_id)
        return os.path.exists(storage_path)

    def get_repository_files(self, repository_id: str, relative_path: str = "") -> List[str]:
        """
        Get list of files in the repository.

        Args:
            repository_id: Repository identifier
            relative_path: Relative path within repository

        Returns:
            List of file paths
        """
        storage_path = self.get_repository_storage_path(repository_id)
        full_path = os.path.join(storage_path, relative_path)

        if not os.path.exists(full_path):
            return []

        files = []
        for root, dirs, filenames in os.walk(full_path):
            # Skip .git directory
            if '.git' in dirs:
                dirs.remove('.git')

            for filename in filenames:
                file_path = os.path.join(root, filename)
                # Make path relative to repository root
                rel_path = os.path.relpath(file_path, storage_path)
                files.append(rel_path)

        return sorted(files)

    def extract_repository_name(self, url: str) -> str:
        """
        Extract repository name from URL.

        Args:
            url: Repository URL

        Returns:
            str: Repository name or 'unknown' if extraction fails
        """
        try:
            repo_info = self._parse_repository_info(url)
            return repo_info['name']
        except (GitOperationError, Exception):
            return "unknown"

    def analyze_repository_structure(self, repo_path: str) -> Tuple[int, int]:
        """
        Analyze repository structure and return file count and total size.

        Args:
            repo_path: Path to the repository

        Returns:
            Tuple of (file_count, total_size)
        """
        file_count = 0
        total_size = 0

        for root, dirs, files in os.walk(repo_path):
            # Skip .git directory
            if '.git' in dirs:
                dirs.remove('.git')

            for file in files:
                file_path = os.path.join(root, file)
                try:
                    total_size += os.path.getsize(file_path)
                    file_count += 1
                except (OSError, IOError):
                    # Skip files we can't access
                    continue

        return file_count, total_size

    def cleanup_repository(self, repo_path: str) -> None:
        """
        Clean up repository directory.

        Args:
            repo_path: Path to the repository to clean up
        """
        try:
            if os.path.exists(repo_path):
                shutil.rmtree(repo_path, ignore_errors=True)
                logger.info(f"Cleaned up repository at: {repo_path}")
        except Exception as e:
            logger.error(f"Failed to cleanup repository {repo_path}: {str(e)}")
"""
Repository management service for handling storage and cleanup operations.
"""

import os
import asyncio
import shutil
from datetime import datetime, timedelta
from typing import List, Optional
import logging

from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..models.repository import Repository, RepositoryVersion
from .git_service import GitService, GitRepositoryInfo

logger = logging.getLogger(__name__)


class RepositoryService:
    """Service for managing repository storage, versioning, and cleanup."""

    def __init__(self, git_service: GitService, storage_limit_gb: int = 50):
        """Initialize repository service.

        Args:
            git_service: Git operations service
            storage_limit_gb: Maximum storage limit in gigabytes
        """
        self.git_service = git_service
        self.storage_limit_bytes = storage_limit_gb * 1024 * 1024 * 1024

    async def check_for_updates(self, db: Session, repository_id: str) -> bool:
        """
        Check if a repository has updates available.

        Args:
            db: Database session
            repository_id: Repository identifier

        Returns:
            bool: True if updates are available
        """
        repository = db.query(Repository).filter(Repository.id == repository_id).first()
        if not repository:
            return False

        # Check if repository exists in storage
        if not self.git_service.repository_exists(repository_id):
            return True  # Repository needs to be cloned again

        try:
            # Get remote HEAD commit
            storage_path = self.git_service.get_repository_storage_path(repository_id)
            from git import Repo

            def get_remote_head():
                repo = Repo(storage_path)
                origin = repo.remotes.origin
                origin.fetch()  # Fetch latest refs
                return str(origin.refs[repository.branch].commit.hexsha)

            loop = asyncio.get_event_loop()
            remote_commit = await loop.run_in_executor(None, get_remote_head)

            # Compare with stored commit hash
            return remote_commit != repository.commit_hash

        except Exception as e:
            logger.error(f"Failed to check updates for repository {repository_id}: {str(e)}")
            return False

    async def create_repository_version(
        self,
        db: Session,
        repository_id: str,
        git_info: GitRepositoryInfo,
        changes_summary: Optional[str] = None
    ) -> str:
        """
        Create a new repository version entry.

        Args:
            db: Database session
            repository_id: Repository identifier
            git_info: Git repository information
            changes_summary: Summary of changes

        Returns:
            str: Version ID
        """
        import uuid

        version_id = str(uuid.uuid4())
        version = RepositoryVersion(
            id=version_id,
            repository_id=repository_id,
            commit_hash=git_info.commit_hash,
            branch=git_info.branch,
            file_count=git_info.file_count,
            total_size=git_info.total_size,
            changes_summary=changes_summary
        )

        db.add(version)
        db.commit()
        logger.info(f"Created version {version_id} for repository {repository_id}")
        return version_id

    async def get_repository_versions(
        self,
        db: Session,
        repository_id: str,
        limit: int = 10
    ) -> List[RepositoryVersion]:
        """
        Get version history for a repository.

        Args:
            db: Database session
            repository_id: Repository identifier
            limit: Maximum number of versions to return

        Returns:
            List of repository versions
        """
        return db.query(RepositoryVersion)\
                .filter(RepositoryVersion.repository_id == repository_id)\
                .order_by(desc(RepositoryVersion.created_at))\
                .limit(limit)\
                .all()

    async def cleanup_old_versions(
        self,
        db: Session,
        repository_id: str,
        keep_versions: int = 5
    ) -> int:
        """
        Clean up old repository versions.

        Args:
            db: Database session
            repository_id: Repository identifier
            keep_versions: Number of versions to keep

        Returns:
            int: Number of versions deleted
        """
        versions = db.query(RepositoryVersion)\
                    .filter(RepositoryVersion.repository_id == repository_id)\
                    .order_by(desc(RepositoryVersion.created_at))\
                    .all()

        if len(versions) <= keep_versions:
            return 0

        versions_to_delete = versions[keep_versions:]
        deleted_count = 0

        for version in versions_to_delete:
            db.delete(version)
            deleted_count += 1

        db.commit()
        logger.info(f"Cleaned up {deleted_count} old versions for repository {repository_id}")
        return deleted_count

    async def get_storage_usage(self) -> dict:
        """
        Get current storage usage statistics.

        Returns:
            dict: Storage usage information
        """
        def calculate_usage():
            total_size = 0
            repo_count = 0

            if os.path.exists(self.git_service.base_storage_path):
                for item in os.listdir(self.git_service.base_storage_path):
                    item_path = os.path.join(self.git_service.base_storage_path, item)
                    if os.path.isdir(item_path):
                        repo_count += 1
                        for root, dirs, files in os.walk(item_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                try:
                                    total_size += os.path.getsize(file_path)
                                except (OSError, IOError):
                                    continue

            return {
                'total_size_bytes': total_size,
                'total_size_gb': total_size / (1024 * 1024 * 1024),
                'repository_count': repo_count,
                'storage_limit_gb': self.storage_limit_bytes / (1024 * 1024 * 1024),
                'usage_percentage': (total_size / self.storage_limit_bytes) * 100 if self.storage_limit_bytes > 0 else 0
            }

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, calculate_usage)

    async def cleanup_storage_if_needed(self, db: Session, threshold_percentage: float = 80.0) -> bool:
        """
        Clean up storage if usage exceeds threshold.

        Args:
            db: Database session
            threshold_percentage: Storage usage threshold for cleanup

        Returns:
            bool: True if cleanup was performed
        """
        usage = await self.get_storage_usage()

        if usage['usage_percentage'] < threshold_percentage:
            return False

        logger.info(f"Storage usage at {usage['usage_percentage']:.1f}%, starting cleanup...")

        # Find repositories that haven't been synced recently
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        old_repos = db.query(Repository)\
                    .filter(
                        (Repository.last_synced_at < cutoff_date) |
                        (Repository.last_synced_at.is_(None))
                    )\
                    .order_by(Repository.total_size.desc())\
                    .limit(5)\
                    .all()

        cleaned_count = 0
        for repo in old_repos:
            if self.git_service.delete_repository(repo.id):
                # Update repository status but don't delete from database
                repo.status = "archived"
                cleaned_count += 1
                logger.info(f"Archived repository {repo.id} to free storage")

        db.commit()

        if cleaned_count > 0:
            logger.info(f"Cleanup completed: archived {cleaned_count} repositories")
            return True

        return False

    async def restore_repository(self, db: Session, repository_id: str) -> bool:
        """
        Restore an archived repository by re-cloning it.

        Args:
            db: Database session
            repository_id: Repository identifier

        Returns:
            bool: True if restoration was successful
        """
        repository = db.query(Repository).filter(Repository.id == repository_id).first()
        if not repository or repository.status != "archived":
            return False

        try:
            # Re-clone the repository
            git_info = await self.git_service.clone_repository(repository.url, repository_id)

            # Update repository information
            repository.status = "active"
            repository.commit_hash = git_info.commit_hash
            repository.file_count = git_info.file_count
            repository.total_size = git_info.total_size
            repository.last_synced_at = datetime.utcnow()

            db.commit()

            # Create new version entry
            await self.create_repository_version(
                db, repository_id, git_info, "Repository restored from archive"
            )

            logger.info(f"Successfully restored repository {repository_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to restore repository {repository_id}: {str(e)}")
            return False
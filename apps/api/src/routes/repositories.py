"""
API routes for repository management.
"""

import uuid
import asyncio
import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from ..database import get_async_db
from ..models.repository import (
    Repository,
    ImportJob,
    RepositoryVersion,
    RepositoryResponse,
    ImportJobResponse,
    RepositoryImportRequest,
    RepositoryImportResponse,
    ImportStatusResponse,
)
from ..services.git_service import GitService, GitOperationError
from ..services.repository_service import RepositoryService
from ..services.processing_service import RepositoryProcessor
from .users import get_current_user
from ..middleware.rate_limiting import apply_rate_limit

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/repositories", tags=["repositories"])

# Initialize services
git_service = GitService()
repository_service = RepositoryService(git_service)
repository_processor = RepositoryProcessor(git_service, repository_service)


# Background task storage for import progress
import_progress = {}


async def update_import_progress(import_id: str, progress: int, message: str):
    """Update import progress in memory and database."""
    import_progress[import_id] = {"progress": progress, "message": message}

    # Also update database
    async with get_async_db().__anext__() as db:
        await db.execute(
            update(ImportJob)
            .where(ImportJob.id == import_id)
            .values(progress=progress, message=message)
        )
        await db.commit()


async def import_repository_background(import_id: str, url: str, repository_id: str, db: AsyncSession):
    """Background task to import a repository."""
    try:
        # Update status to cloning
        await db.execute(
            update(ImportJob)
            .where(ImportJob.id == import_id)
            .values(status="cloning", message="Starting clone operation...")
        )
        await db.commit()

        # Create progress callback
        async def progress_callback(progress: int, message: str):
            await update_import_progress(import_id, progress, message)

        # Clone the repository
        repo_info = await git_service.clone_repository(
            url, repository_id, progress_callback
        )

        # Update status to processing
        await db.execute(
            update(ImportJob)
            .where(ImportJob.id == import_id)
            .values(status="processing", message="Processing repository data...")
        )
        await db.commit()

        # Create repository record
        repository = Repository(
            id=repository_id,
            name=repo_info.name,
            owner=repo_info.owner,
            url=repo_info.url,
            description=repo_info.description,
            branch=repo_info.branch,
            commit_hash=repo_info.commit_hash,
            file_count=repo_info.file_count,
            total_size=repo_info.total_size,
            status="active",
            imported_at=datetime.utcnow(),
        )

        # Get user email from import job
        result = await db.execute(select(ImportJob).where(ImportJob.id == import_id))
        import_job = result.scalar_one()
        repository.user_email = import_job.user_email

        db.add(repository)

        # Update import job to completed
        await db.execute(
            update(ImportJob)
            .where(ImportJob.id == import_id)
            .values(
                status="completed",
                progress=100,
                message="Repository imported successfully!",
                completed_at=datetime.utcnow(),
            )
        )

        await db.commit()

        # Clean up progress tracking
        import_progress.pop(import_id, None)

    except GitOperationError as e:
        # Handle Git-specific errors
        await db.execute(
            update(ImportJob)
            .where(ImportJob.id == import_id)
            .values(
                status="failed",
                message="Import failed",
                error_message=str(e),
                completed_at=datetime.utcnow(),
            )
        )
        await db.commit()
        import_progress.pop(import_id, None)

    except Exception as e:
        # Handle unexpected errors
        await db.execute(
            update(ImportJob)
            .where(ImportJob.id == import_id)
            .values(
                status="failed",
                message="Unexpected error during import",
                error_message=str(e),
                completed_at=datetime.utcnow(),
            )
        )
        await db.commit()
        import_progress.pop(import_id, None)


@router.post("/import", response_model=RepositoryImportResponse)
async def import_repository(
    request: RepositoryImportRequest,
    http_request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(get_current_user),
):
    """
    Start importing a Git repository.

    This endpoint validates the repository URL and starts a background import process.
    Use the returned import_id to check the progress via GET /repositories/{import_id}/status
    """
    # Apply rate limiting for repository imports (10 per minute)
    await apply_rate_limit(
        http_request,
        current_user["id"],
        limit=10,
        window=60,
        endpoint_key="repository_import"
    )

    # Validate URL format
    if not git_service.validate_repository_url(request.url):
        raise HTTPException(
            status_code=400,
            detail="Invalid repository URL. Supported: GitHub, GitLab, Bitbucket"
        )

    # Generate unique IDs
    import_id = str(uuid.uuid4())
    repository_id = str(uuid.uuid4())

    # Create import job record
    import_job = ImportJob(
        id=import_id,
        repository_id=repository_id,
        url=request.url,
        status="pending",
        progress=0,
        message="Import request received",
        started_at=datetime.utcnow(),
        user_email=current_user.email,
    )

    db.add(import_job)
    await db.commit()

    # Start background import
    background_tasks.add_task(
        import_repository_background, import_id, request.url, repository_id, db
    )

    return RepositoryImportResponse(
        import_id=import_id,
        message="Import started. Use the import_id to check progress."
    )


@router.get("/{import_id}/status", response_model=ImportStatusResponse)
async def get_import_status(
    import_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Get the status of a repository import operation.

    Returns the current progress, status, and repository information if completed.
    """
    # Get import job from database
    result = await db.execute(select(ImportJob).where(ImportJob.id == import_id))
    import_job = result.scalar_one_or_none()

    if not import_job:
        raise HTTPException(status_code=404, detail="Import job not found")

    # Check for in-memory progress updates
    if import_id in import_progress:
        progress_data = import_progress[import_id]
        current_progress = progress_data["progress"]
        current_message = progress_data["message"]
    else:
        current_progress = import_job.progress
        current_message = import_job.message

    response_data = {
        "id": import_job.id,
        "status": import_job.status,
        "progress": current_progress,
        "message": current_message,
    }

    # If completed, include repository information
    if import_job.status == "completed":
        result = await db.execute(
            select(Repository).where(Repository.id == import_job.repository_id)
        )
        repository = result.scalar_one_or_none()

        if repository:
            response_data["repository"] = RepositoryResponse.from_orm(repository)

    return ImportStatusResponse(**response_data)


@router.get("", response_model=List[RepositoryResponse])
async def list_repositories(
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0,
):
    """
    List user's imported repositories.

    Returns a paginated list of repositories owned by the current user.
    """
    result = await db.execute(
        select(Repository)
        .where(Repository.user_email == current_user.email)
        .order_by(Repository.imported_at.desc())
        .limit(limit)
        .offset(offset)
    )
    repositories = result.scalars().all()

    return [RepositoryResponse.from_orm(repo) for repo in repositories]


@router.get("/{repository_id}", response_model=RepositoryResponse)
async def get_repository(
    repository_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    """Get details of a specific repository."""
    result = await db.execute(select(Repository).where(Repository.id == repository_id))
    repository = result.scalar_one_or_none()

    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")

    return RepositoryResponse.from_orm(repository)


@router.put("/{repository_id}/sync")
async def sync_repository(
    repository_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Synchronize a repository with its remote origin.

    This pulls the latest changes from the remote repository.
    """
    # Check if repository exists
    result = await db.execute(select(Repository).where(Repository.id == repository_id))
    repository = result.scalar_one_or_none()

    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")

    # Update status to syncing
    await db.execute(
        update(Repository)
        .where(Repository.id == repository_id)
        .values(status="syncing")
    )
    await db.commit()

    async def sync_background():
        try:
            # Update repository with latest changes
            repo_info = await git_service.update_repository(repository_id)

            # Update database record
            await db.execute(
                update(Repository)
                .where(Repository.id == repository_id)
                .values(
                    commit_hash=repo_info.commit_hash,
                    file_count=repo_info.file_count,
                    total_size=repo_info.total_size,
                    description=repo_info.description,
                    status="active",
                    last_synced_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
            )
            await db.commit()

        except GitOperationError:
            # Update status to error
            await db.execute(
                update(Repository)
                .where(Repository.id == repository_id)
                .values(status="error")
            )
            await db.commit()

    background_tasks.add_task(sync_background)

    return {"message": "Repository sync started"}


@router.delete("/{repository_id}")
async def delete_repository(
    repository_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Delete a repository and all its data.

    This removes both the database record and the local repository files.
    """
    # Check if repository exists
    result = await db.execute(select(Repository).where(Repository.id == repository_id))
    repository = result.scalar_one_or_none()

    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")

    # Delete from file system
    if git_service.repository_exists(repository_id):
        git_service.delete_repository(repository_id)

    # Delete from database
    await db.execute(
        Repository.__table__.delete().where(Repository.id == repository_id)
    )

    # Also clean up any related import jobs
    await db.execute(
        ImportJob.__table__.delete().where(ImportJob.repository_id == repository_id)
    )

    await db.commit()

    return {"message": "Repository deleted successfully"}


@router.get("/{repository_id}/versions")
async def get_repository_versions(
    repository_id: str,
    db: AsyncSession = Depends(get_async_db),
    limit: int = 10,
):
    """Get version history for a repository."""
    # Check if repository exists
    result = await db.execute(select(Repository).where(Repository.id == repository_id))
    repository = result.scalar_one_or_none()

    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")

    # Get versions
    versions_result = await db.execute(
        select(RepositoryVersion)
        .where(RepositoryVersion.repository_id == repository_id)
        .order_by(RepositoryVersion.created_at.desc())
        .limit(limit)
    )
    versions = versions_result.scalars().all()

    return [
        {
            "id": version.id,
            "commit_hash": version.commit_hash,
            "branch": version.branch,
            "file_count": version.file_count,
            "total_size": version.total_size,
            "changes_summary": version.changes_summary,
            "created_at": version.created_at,
        }
        for version in versions
    ]


@router.post("/{repository_id}/check-updates")
async def check_repository_updates(
    repository_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    """Check if a repository has updates available."""
    # Check if repository exists
    result = await db.execute(select(Repository).where(Repository.id == repository_id))
    repository = result.scalar_one_or_none()

    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")

    # Check for updates using repository service
    has_updates = await repository_service.check_for_updates(db, repository_id)

    return {
        "repository_id": repository_id,
        "has_updates": has_updates,
        "current_commit": repository.commit_hash,
        "last_synced": repository.last_synced_at
    }


@router.get("/storage/usage")
async def get_storage_usage():
    """Get current storage usage statistics."""
    usage = await repository_service.get_storage_usage()
    return usage


@router.post("/storage/cleanup")
async def cleanup_storage(
    db: AsyncSession = Depends(get_async_db),
    threshold: float = 80.0
):
    """Clean up storage if usage exceeds threshold."""
    cleanup_performed = await repository_service.cleanup_storage_if_needed(db, threshold)

    if cleanup_performed:
        usage = await repository_service.get_storage_usage()
        return {
            "cleanup_performed": True,
            "message": "Storage cleanup completed",
            "current_usage": usage
        }
    else:
        return {
            "cleanup_performed": False,
            "message": "Storage cleanup not needed"
        }


@router.put("/{repository_id}/restore")
async def restore_repository(
    repository_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    """Restore an archived repository by re-cloning it."""
    success = await repository_service.restore_repository(db, repository_id)

    if success:
        return {"message": "Repository restored successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to restore repository or repository not archived")


@router.post("/{repository_id}/process")
async def process_repository(
    repository_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(get_current_user),
):
    """
    Process a repository through the complete analysis pipeline.

    Analyzes repository structure, documentation, source code, and extracts metadata.
    """
    # Check if repository exists and belongs to user
    result = await db.execute(
        select(Repository)
        .where(
            Repository.id == repository_id,
            Repository.user_email == current_user.email
        )
    )
    repository = result.scalar_one_or_none()

    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found or access denied")

    # Create processing job (reuse import job structure for now)
    processing_id = str(uuid.uuid4())
    processing_job = ImportJob(
        id=processing_id,
        repository_id=repository_id,
        url=repository.url,
        status="pending",
        progress=0,
        message="Repository processing started",
        started_at=datetime.utcnow(),
        user_email=current_user.email,
    )

    db.add(processing_job)
    await db.commit()

    # Progress tracking for processing
    async def processing_progress(progress: int, message: str):
        import_progress[processing_id] = {"progress": progress, "message": message}
        await db.execute(
            update(ImportJob)
            .where(ImportJob.id == processing_id)
            .values(progress=progress, message=message)
        )
        await db.commit()

    # Background processing task
    async def process_background():
        try:
            # Process repository
            processing_results = await repository_processor.process_repository(
                db, repository_id, processing_progress
            )

            # Update job status
            await db.execute(
                update(ImportJob)
                .where(ImportJob.id == processing_id)
                .values(
                    status="completed",
                    progress=100,
                    message="Repository processing completed",
                    completed_at=datetime.utcnow(),
                )
            )
            await db.commit()

            # Store processing results (could extend to dedicated table)
            logger.info(f"Repository {repository_id} processing completed: {processing_results['processing_stats']}")

        except Exception as e:
            await db.execute(
                update(ImportJob)
                .where(ImportJob.id == processing_id)
                .values(
                    status="failed",
                    message="Processing failed",
                    error_message=str(e),
                    completed_at=datetime.utcnow(),
                )
            )
            await db.commit()

    background_tasks.add_task(process_background)

    return {
        "processing_id": processing_id,
        "message": "Repository processing started",
        "repository_id": repository_id
    }


@router.get("/{repository_id}/files")
async def list_repository_files(
    repository_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(get_current_user),
    path: str = "",
):
    """
    List files in a repository directory.

    Provides file browsing capability for processed repositories.
    """
    # Check if repository exists and belongs to user
    result = await db.execute(
        select(Repository)
        .where(
            Repository.id == repository_id,
            Repository.user_email == current_user.email
        )
    )
    repository = result.scalar_one_or_none()

    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found or access denied")

    # Get file list
    files = git_service.get_repository_files(repository_id, path)

    return {
        "repository_id": repository_id,
        "path": path,
        "files": files,
        "file_count": len(files)
    }


@router.post("/test/magnet")
async def test_magnet_repository(
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(get_current_user),
):
    """
    Test processing pipeline with magnet repository structure.

    This endpoint is for validating the processing pipeline as required by AC 6.
    """
    # This would typically import the ./projects/magnet repository first
    # For now, return a test structure validation
    test_results = {
        "test_name": "magnet_repository_processing",
        "status": "ready_for_testing",
        "requirements": [
            "Import ./projects/magnet repository via /api/repositories/import",
            "Run processing pipeline via /api/repositories/{id}/process",
            "Validate file structure preservation",
            "Verify documentation extraction",
            "Confirm source code analysis"
        ],
        "message": "Use standard import and process endpoints to test with magnet repository"
    }

    return test_results
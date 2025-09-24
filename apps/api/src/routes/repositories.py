"""
API routes for repository management.
"""

import uuid
import asyncio
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from ..database import get_async_db
from ..models.repository import (
    Repository,
    ImportJob,
    RepositoryResponse,
    ImportJobResponse,
    RepositoryImportRequest,
    RepositoryImportResponse,
    ImportStatusResponse,
)
from ..services.git_service import GitService, GitOperationError

router = APIRouter(prefix="/api/repositories", tags=["repositories"])

# Initialize Git service
git_service = GitService()


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
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Start importing a Git repository.

    This endpoint validates the repository URL and starts a background import process.
    Use the returned import_id to check the progress via GET /repositories/{import_id}/status
    """
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
    limit: int = 50,
    offset: int = 0,
):
    """
    List all imported repositories.

    Returns a paginated list of repositories with their metadata and status.
    """
    result = await db.execute(
        select(Repository)
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
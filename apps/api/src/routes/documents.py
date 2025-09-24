"""
Document management endpoints for DocGraph API
"""
from typing import List

from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse

from ..models.base import BaseSchema

router = APIRouter()


class DocumentSchema(BaseSchema):
    """
    Document schema for API responses.
    TODO: Move to proper models module when database integration is added.
    """
    id: str
    title: str
    content: str
    file_type: str


class DocumentCreateSchema(BaseSchema):
    """
    Schema for creating new documents.
    """
    title: str
    content: str
    file_type: str = "text"


@router.get(
    "",
    response_model=List[DocumentSchema],
    status_code=status.HTTP_200_OK,
    summary="List Documents",
    description="Retrieve a list of all documents"
)
async def list_documents():
    """
    Get a list of all documents in the system.
    TODO: Implement actual database query.
    """
    # Mock data for now
    mock_documents = [
        {
            "id": "1",
            "title": "Sample Document",
            "content": "This is a sample document for testing the DocGraph system.",
            "file_type": "text"
        },
        {
            "id": "2",
            "title": "Another Document",
            "content": "This is another sample document.",
            "file_type": "text"
        }
    ]

    return JSONResponse(
        content=mock_documents,
        status_code=status.HTTP_200_OK
    )


@router.get(
    "/{document_id}",
    response_model=DocumentSchema,
    status_code=status.HTTP_200_OK,
    summary="Get Document",
    description="Retrieve a specific document by ID"
)
async def get_document(document_id: str):
    """
    Get a specific document by its ID.
    TODO: Implement actual database query.
    """
    # Mock data for now
    if document_id == "1":
        mock_document = {
            "id": "1",
            "title": "Sample Document",
            "content": "This is a sample document for testing the DocGraph system.",
            "file_type": "text"
        }
        return JSONResponse(
            content=mock_document,
            status_code=status.HTTP_200_OK
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )


@router.post(
    "",
    response_model=DocumentSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create Document",
    description="Create a new document"
)
async def create_document(document: DocumentCreateSchema):
    """
    Create a new document.
    TODO: Implement actual database insertion.
    """
    # Mock creation for now
    new_document = {
        "id": "new_doc_123",
        "title": document.title,
        "content": document.content,
        "file_type": document.file_type
    }

    return JSONResponse(
        content=new_document,
        status_code=status.HTTP_201_CREATED
    )
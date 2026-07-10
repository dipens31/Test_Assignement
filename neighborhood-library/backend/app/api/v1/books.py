import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.book import BookCreate, BookResponse, BookUpdate
from app.schemas.common import PaginatedResponse
from app.services.book_service import BookService

router = APIRouter(prefix="/books", tags=["Books"])


def get_book_service(db: Session = Depends(get_db)) -> BookService:
    return BookService(db)


@router.post(
    "",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new book",
)
def create_book(
    payload: BookCreate,
    svc: BookService = Depends(get_book_service),
):
    return svc.create(payload)


@router.get(
    "",
    response_model=PaginatedResponse[BookResponse],
    summary="List / search books",
)
def list_books(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    title: Optional[str] = Query(default=None, description="Partial title search"),
    author: Optional[str] = Query(default=None, description="Partial author search"),
    available_only: bool = Query(default=False, description="Filter to only available books"),
    svc: BookService = Depends(get_book_service),
):
    total, items = svc.list(skip=skip, limit=limit, title=title, author=author, available_only=available_only)
    return PaginatedResponse(total=total, skip=skip, limit=limit, items=items)


@router.get(
    "/{book_id}",
    response_model=BookResponse,
    summary="Get a single book by ID",
)
def get_book(
    book_id: uuid.UUID,
    svc: BookService = Depends(get_book_service),
):
    return svc.get(book_id)


@router.put(
    "/{book_id}",
    response_model=BookResponse,
    summary="Update an existing book",
)
def update_book(
    book_id: uuid.UUID,
    payload: BookUpdate,
    svc: BookService = Depends(get_book_service),
):
    return svc.update(book_id, payload)

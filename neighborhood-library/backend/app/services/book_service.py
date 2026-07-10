import uuid
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.book import Book
from app.repositories.book_repository import BookRepository
from app.schemas.book import BookCreate, BookUpdate


class BookService:
    def __init__(self, db: Session):
        self.repo = BookRepository(db)

    def create(self, payload: BookCreate) -> Book:
        if payload.isbn:
            existing = self.repo.get_by_isbn(payload.isbn)
            if existing:
                raise ConflictError(f"A book with ISBN '{payload.isbn}' already exists.")
        return self.repo.create(
            title=payload.title,
            author=payload.author,
            isbn=payload.isbn,
            published_year=payload.published_year,
            copies_total=payload.copies_total,
        )

    def get(self, book_id: uuid.UUID) -> Book:
        book = self.repo.get_by_id(book_id)
        if not book:
            raise NotFoundError("Book", str(book_id))
        return book

    def update(self, book_id: uuid.UUID, payload: BookUpdate) -> Book:
        book = self.get(book_id)

        if payload.isbn and payload.isbn != book.isbn:
            existing = self.repo.get_by_isbn(payload.isbn)
            if existing:
                raise ConflictError(f"A book with ISBN '{payload.isbn}' already exists.")

        update_data = payload.model_dump(exclude_unset=True, exclude_none=True)

        if "copies_total" in update_data:
            new_total = update_data["copies_total"]
            checked_out = book.copies_total - book.copies_available
            if new_total < checked_out:
                raise ConflictError(
                    f"Cannot reduce copies_total to {new_total}: "
                    f"{checked_out} copies are currently checked out."
                )
            diff = new_total - book.copies_total
            update_data["copies_available"] = book.copies_available + diff

        return self.repo.update(book, **update_data)

    def list(
        self,
        skip: int = 0,
        limit: int = 20,
        title: Optional[str] = None,
        author: Optional[str] = None,
        available_only: bool = False,
    ) -> Tuple[int, List[Book]]:
        return self.repo.list(skip=skip, limit=limit, title=title, author=author, available_only=available_only)

import uuid
from typing import List, Optional, Tuple

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.book import Book


class BookRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, title: str, author: str, isbn: Optional[str], published_year: Optional[int], copies_total: int) -> Book:
        book = Book(
            title=title,
            author=author,
            isbn=isbn,
            published_year=published_year,
            copies_total=copies_total,
            copies_available=copies_total,
        )
        self.db.add(book)
        self.db.commit()
        self.db.refresh(book)
        return book

    def get_by_id(self, book_id: uuid.UUID) -> Optional[Book]:
        return self.db.query(Book).filter(Book.id == book_id).first()

    def get_by_id_for_update(self, book_id: uuid.UUID) -> Optional[Book]:
        return self.db.query(Book).filter(Book.id == book_id).with_for_update().first()

    def get_by_isbn(self, isbn: str) -> Optional[Book]:
        return self.db.query(Book).filter(Book.isbn == isbn).first()

    def list(
        self,
        skip: int = 0,
        limit: int = 20,
        title: Optional[str] = None,
        author: Optional[str] = None,
        available_only: bool = False,
    ) -> Tuple[int, List[Book]]:
        query = self.db.query(Book)

        if title:
            query = query.filter(Book.title.ilike(f"%{title}%"))
        if author:
            query = query.filter(Book.author.ilike(f"%{author}%"))
        if available_only:
            query = query.filter(Book.copies_available > 0)

        total = query.count()
        items = query.order_by(Book.title).offset(skip).limit(limit).all()
        return total, items

    def update(self, book: Book, **kwargs) -> Book:
        for key, value in kwargs.items():
            if value is not None:
                setattr(book, key, value)
        self.db.commit()
        self.db.refresh(book)
        return book

    def delete(self, book: Book) -> None:
        self.db.delete(book)
        self.db.commit()

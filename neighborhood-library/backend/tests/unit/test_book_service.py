"""
Unit tests for BookService using a mocked repository.
"""
import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.core.exceptions import ConflictError, NotFoundError
from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate
from app.services.book_service import BookService


def make_book(**kwargs) -> Book:
    defaults = dict(
        id=uuid.uuid4(),
        title="Test Book",
        author="Test Author",
        isbn=None,
        published_year=2020,
        copies_total=3,
        copies_available=3,
    )
    defaults.update(kwargs)
    b = Book()
    for k, v in defaults.items():
        setattr(b, k, v)
    return b


@pytest.fixture
def svc(mock_db):
    return BookService(mock_db)


class TestBookServiceCreate:
    def test_create_without_isbn(self, svc):
        svc.repo.get_by_isbn = MagicMock(return_value=None)
        svc.repo.create = MagicMock(return_value=make_book())
        payload = BookCreate(title="A", author="B", copies_total=2)
        result = svc.create(payload)
        svc.repo.create.assert_called_once()
        assert result is not None

    def test_create_with_unique_isbn(self, svc):
        svc.repo.get_by_isbn = MagicMock(return_value=None)
        svc.repo.create = MagicMock(return_value=make_book(isbn="978-0-13-595705-9"))
        payload = BookCreate(title="A", author="B", isbn="978-0-13-595705-9", copies_total=1)
        result = svc.create(payload)
        svc.repo.create.assert_called_once()

    def test_create_raises_conflict_on_duplicate_isbn(self, svc):
        svc.repo.get_by_isbn = MagicMock(return_value=make_book(isbn="dup-isbn"))
        payload = BookCreate(title="A", author="B", isbn="dup-isbn", copies_total=1)
        with pytest.raises(ConflictError):
            svc.create(payload)


class TestBookServiceGet:
    def test_get_existing_book(self, svc):
        book = make_book()
        svc.repo.get_by_id = MagicMock(return_value=book)
        result = svc.get(book.id)
        assert result.id == book.id

    def test_get_missing_book_raises_not_found(self, svc):
        svc.repo.get_by_id = MagicMock(return_value=None)
        with pytest.raises(NotFoundError):
            svc.get(uuid.uuid4())


class TestBookServiceUpdate:
    def test_update_title(self, svc):
        book = make_book()
        updated = make_book(id=book.id, title="New Title")
        svc.repo.get_by_id = MagicMock(return_value=book)
        svc.repo.get_by_isbn = MagicMock(return_value=None)
        svc.repo.update = MagicMock(return_value=updated)
        result = svc.update(book.id, BookUpdate(title="New Title"))
        assert result.title == "New Title"

    def test_update_copies_total_increase(self, svc):
        book = make_book(copies_total=3, copies_available=2)
        svc.repo.get_by_id = MagicMock(return_value=book)
        svc.repo.get_by_isbn = MagicMock(return_value=None)
        svc.repo.update = MagicMock(return_value=book)
        svc.update(book.id, BookUpdate(copies_total=5))
        call_kwargs = svc.repo.update.call_args[1]
        assert call_kwargs["copies_available"] == 4  # 2 + (5-3)

    def test_update_copies_total_cannot_go_below_checked_out(self, svc):
        book = make_book(copies_total=5, copies_available=1)  # 4 checked out
        svc.repo.get_by_id = MagicMock(return_value=book)
        with pytest.raises(ConflictError):
            svc.update(book.id, BookUpdate(copies_total=3))  # < 4 out

    def test_update_isbn_conflict(self, svc):
        book = make_book(isbn="old-isbn")
        svc.repo.get_by_id = MagicMock(return_value=book)
        svc.repo.get_by_isbn = MagicMock(return_value=make_book(isbn="new-isbn"))
        with pytest.raises(ConflictError):
            svc.update(book.id, BookUpdate(isbn="new-isbn"))

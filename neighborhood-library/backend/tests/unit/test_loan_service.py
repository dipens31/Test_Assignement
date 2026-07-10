"""
Unit tests for LoanService business logic using mocked repositories.
"""
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.models.book import Book
from app.models.loan import Loan, LoanStatus
from app.models.member import Member
from app.schemas.loan import BorrowRequest, ReturnRequest
from app.services.loan_service import LoanService


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_member(**kw) -> Member:
    m = Member()
    m.id = kw.get("id", uuid.uuid4())
    m.name = kw.get("name", "Alice")
    m.email = kw.get("email", "alice@example.com")
    return m


def make_book(**kw) -> Book:
    b = Book()
    b.id = kw.get("id", uuid.uuid4())
    b.title = kw.get("title", "Test Book")
    b.author = kw.get("author", "Author")
    b.copies_total = kw.get("copies_total", 3)
    b.copies_available = kw.get("copies_available", 3)
    return b


def make_loan(**kw) -> Loan:
    l = Loan()  # noqa: E741
    l.id = kw.get("id", uuid.uuid4())
    l.member_id = kw.get("member_id", uuid.uuid4())
    l.book_id = kw.get("book_id", uuid.uuid4())
    l.borrowed_at = kw.get("borrowed_at", datetime.now(timezone.utc) - timedelta(days=10))
    l.due_at = kw.get("due_at", None)
    l.returned_at = kw.get("returned_at", None)
    l.status = kw.get("status", LoanStatus.BORROWED)
    l.fine_amount = kw.get("fine_amount", 0)
    return l


@pytest.fixture
def svc(mock_db):
    s = LoanService(mock_db)
    s.loan_repo = MagicMock()
    s.book_repo = MagicMock()
    s.member_repo = MagicMock()
    return s


# ── Borrow tests ──────────────────────────────────────────────────────────────

class TestBorrowBook:
    def test_borrow_success(self, svc):
        member = make_member()
        book = make_book(copies_available=2)
        loan = make_loan(member_id=member.id, book_id=book.id)

        svc.member_repo.get_by_id.return_value = member
        svc.book_repo.get_by_id_for_update.return_value = book
        svc.loan_repo.get_active_loan_for_member_book.return_value = None  # No existing active loan
        svc.loan_repo.create.return_value = loan

        payload = BorrowRequest(member_id=member.id, book_id=book.id)
        result = svc.borrow(payload)

        assert result is loan
        assert book.copies_available == 1
        svc.loan_repo.create.assert_called_once()

    def test_borrow_decrements_copies_available(self, svc):
        member = make_member()
        book = make_book(copies_available=5)
        svc.member_repo.get_by_id.return_value = member
        svc.book_repo.get_by_id_for_update.return_value = book
        svc.loan_repo.get_active_loan_for_member_book.return_value = None  # No existing active loan
        svc.loan_repo.create.return_value = make_loan()

        svc.borrow(BorrowRequest(member_id=member.id, book_id=book.id))
        assert book.copies_available == 4

    def test_borrow_member_not_found(self, svc):
        svc.member_repo.get_by_id.return_value = None
        with pytest.raises(NotFoundError):
            svc.borrow(BorrowRequest(member_id=uuid.uuid4(), book_id=uuid.uuid4()))

    def test_borrow_book_not_found(self, svc):
        svc.member_repo.get_by_id.return_value = make_member()
        svc.book_repo.get_by_id_for_update.return_value = None
        svc.loan_repo.get_active_loan_for_member_book.return_value = None  # No existing active loan
        with pytest.raises(NotFoundError):
            svc.borrow(BorrowRequest(member_id=uuid.uuid4(), book_id=uuid.uuid4()))

    def test_borrow_no_copies_available(self, svc):
        member = make_member()
        book = make_book(copies_available=0)
        svc.member_repo.get_by_id.return_value = member
        svc.book_repo.get_by_id_for_update.return_value = book
        svc.loan_repo.get_active_loan_for_member_book.return_value = None  # No existing active loan
        with pytest.raises(ConflictError):
            svc.borrow(BorrowRequest(member_id=member.id, book_id=book.id))

    def test_borrow_with_future_due_date(self, svc):
        member = make_member()
        book = make_book(copies_available=1)
        loan = make_loan()
        svc.member_repo.get_by_id.return_value = member
        svc.book_repo.get_by_id_for_update.return_value = book
        svc.loan_repo.get_active_loan_for_member_book.return_value = None  # No existing active loan
        svc.loan_repo.create.return_value = loan

        future = datetime.now(timezone.utc) + timedelta(days=14)
        result = svc.borrow(BorrowRequest(member_id=member.id, book_id=book.id, due_at=future))
        assert result is loan

    def test_borrow_rejects_past_due_date(self, svc):
        member = make_member()
        book = make_book(copies_available=1)
        svc.member_repo.get_by_id.return_value = member
        svc.book_repo.get_by_id_for_update.return_value = book
        svc.loan_repo.get_active_loan_for_member_book.return_value = None  # No existing active loan

        past = datetime.now(timezone.utc) - timedelta(days=1)
        with pytest.raises(ValueError):  # Pydantic validation raises ValueError
            svc.borrow(BorrowRequest(member_id=member.id, book_id=book.id, due_at=past))


# ── Return tests ──────────────────────────────────────────────────────────────

class TestReturnBook:
    def test_return_success_no_fine(self, svc):
        due = datetime.now(timezone.utc) + timedelta(days=7)
        loan = make_loan(due_at=due, status=LoanStatus.BORROWED)
        book = make_book(copies_available=0)

        svc.loan_repo.get_by_id_for_update.return_value = loan
        svc.book_repo.get_by_id_for_update.return_value = book
        svc.loan_repo.save.return_value = loan

        result = svc.return_book(ReturnRequest(loan_id=loan.id))
        assert result.status == LoanStatus.RETURNED
        assert float(result.fine_amount) == 0.0
        assert book.copies_available == 1

    def test_return_success_with_fine(self, svc):
        past_due = datetime.now(timezone.utc) - timedelta(days=5)
        loan = make_loan(due_at=past_due, status=LoanStatus.BORROWED)
        book = make_book(copies_available=0)

        svc.loan_repo.get_by_id_for_update.return_value = loan
        svc.book_repo.get_by_id_for_update.return_value = book
        svc.loan_repo.save.return_value = loan

        result = svc.return_book(ReturnRequest(loan_id=loan.id))
        assert result.status == LoanStatus.RETURNED
        assert float(result.fine_amount) >= 2.50  # at least 5 days × $0.50

    def test_return_increments_copies_available(self, svc):
        loan = make_loan(status=LoanStatus.BORROWED)
        book = make_book(copies_available=0)
        svc.loan_repo.get_by_id_for_update.return_value = loan
        svc.book_repo.get_by_id_for_update.return_value = book
        svc.loan_repo.save.return_value = loan

        svc.return_book(ReturnRequest(loan_id=loan.id))
        assert book.copies_available == 1

    def test_return_loan_not_found(self, svc):
        svc.loan_repo.get_by_id_for_update.return_value = None
        with pytest.raises(NotFoundError):
            svc.return_book(ReturnRequest(loan_id=uuid.uuid4()))

    def test_return_already_returned_raises_bad_request(self, svc):
        loan = make_loan(status=LoanStatus.RETURNED)
        svc.loan_repo.get_by_id_for_update.return_value = loan
        with pytest.raises(BadRequestError):
            svc.return_book(ReturnRequest(loan_id=loan.id))

    def test_return_sets_returned_at(self, svc):
        loan = make_loan(status=LoanStatus.BORROWED)
        book = make_book()
        svc.loan_repo.get_by_id_for_update.return_value = loan
        svc.book_repo.get_by_id_for_update.return_value = book
        svc.loan_repo.save.return_value = loan

        svc.return_book(ReturnRequest(loan_id=loan.id))
        assert loan.returned_at is not None


# ── Overdue tests ─────────────────────────────────────────────────────────────

class TestGetOverdue:
    def test_overdue_loans_get_status_set(self, svc):
        past_due = datetime.now(timezone.utc) - timedelta(days=3)
        loan = make_loan(due_at=past_due, status=LoanStatus.BORROWED)
        svc.loan_repo.get_overdue.return_value = [loan]

        results = svc.get_overdue()
        assert len(results) == 1
        assert results[0].status == LoanStatus.OVERDUE

    def test_overdue_fine_is_calculated(self, svc):
        past_due = datetime.now(timezone.utc) - timedelta(days=4)
        loan = make_loan(due_at=past_due, status=LoanStatus.BORROWED)
        svc.loan_repo.get_overdue.return_value = [loan]

        results = svc.get_overdue()
        assert float(results[0].fine_amount) >= 2.00  # at least 4 × $0.50

    def test_no_overdue_loans(self, svc):
        svc.loan_repo.get_overdue.return_value = []
        results = svc.get_overdue()
        assert results == []

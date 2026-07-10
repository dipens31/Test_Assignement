"""
Shared test fixtures for unit and integration tests.

Integration tests use a real PostgreSQL database (library_test) with
per-test transaction rollback for isolation.
Unit tests use MagicMock for the DB session – no real DB needed.
"""
import os
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app
from app.models.book import Book
from app.models.loan import Loan, LoanStatus
from app.models.member import Member

# ── Test database ─────────────────────────────────────────────────────────────
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://library_user:library_password@localhost:5432/library_test",
)

test_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# ── Session-scoped: create / drop schema once per test run ───────────────────
@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


# ── Function-scoped: wrap each test in a transaction, roll back afterwards ───
@pytest.fixture
def db():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


# ── FastAPI test client that injects the rollback-wrapped session ─────────────
@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── Convenience factory fixtures ──────────────────────────────────────────────
@pytest.fixture
def make_book(db):
    """Factory to insert a book directly into the test DB."""

    def _make(
        title="Test Book",
        author="Test Author",
        isbn=None,
        copies_total=3,
        copies_available=None,
    ):
        book = Book(
            id=uuid.uuid4(),
            title=title,
            author=author,
            isbn=isbn,
            copies_total=copies_total,
            copies_available=copies_total if copies_available is None else copies_available,
        )
        db.add(book)
        db.flush()
        return book

    return _make


@pytest.fixture
def make_member(db):
    """Factory to insert a member directly into the test DB."""

    def _make(name="Alice", email=None):
        email = email or f"test_{uuid.uuid4().hex[:8]}@example.com"
        member = Member(id=uuid.uuid4(), name=name, email=email)
        db.add(member)
        db.flush()
        return member

    return _make


@pytest.fixture
def make_loan(db):
    """Factory to insert a loan directly into the test DB."""

    def _make(member, book, status=LoanStatus.BORROWED, due_at=None, returned_at=None, fine_amount=0):
        loan = Loan(
            id=uuid.uuid4(),
            member_id=member.id,
            book_id=book.id,
            borrowed_at=datetime.now(timezone.utc) - timedelta(days=7),
            due_at=due_at,
            returned_at=returned_at,
            status=status,
            fine_amount=fine_amount,
        )
        db.add(loan)
        db.flush()
        return loan

    return _make


# ── Mock DB session for pure-unit tests ──────────────────────────────────────
@pytest.fixture
def mock_db():
    return MagicMock()

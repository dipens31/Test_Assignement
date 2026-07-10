"""
Integration tests for /api/v1/loans endpoints (borrow, return, list, overdue)
and /api/v1/members/{id}/loans.
"""
import uuid
from datetime import datetime, timedelta, timezone

import pytest


class TestBorrowBook:
    def test_borrow_success(self, client, make_book, make_member):
        book = make_book(copies_total=2)
        member = make_member()
        resp = client.post("/api/v1/loans/borrow", json={
            "member_id": str(member.id),
            "book_id": str(book.id),
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "BORROWED"
        assert data["returned_at"] is None
        assert float(data["fine_amount"]) == 0.0

    def test_borrow_decreases_copies_available(self, client, make_book, make_member, db):
        book = make_book(copies_total=3)
        member = make_member()
        client.post("/api/v1/loans/borrow", json={
            "member_id": str(member.id),
            "book_id": str(book.id),
        })
        db.refresh(book)
        assert book.copies_available == 2

    def test_borrow_with_due_date(self, client, make_book, make_member):
        book = make_book()
        member = make_member()
        future = (datetime.now(timezone.utc) + timedelta(days=14)).isoformat()
        resp = client.post("/api/v1/loans/borrow", json={
            "member_id": str(member.id),
            "book_id": str(book.id),
            "due_at": future,
        })
        assert resp.status_code == 201
        assert resp.json()["due_at"] is not None

    def test_borrow_unavailable_book_returns_409(self, client, make_book, make_member):
        book = make_book(copies_total=1, copies_available=0)
        member = make_member()
        resp = client.post("/api/v1/loans/borrow", json={
            "member_id": str(member.id),
            "book_id": str(book.id),
        })
        assert resp.status_code == 409
        assert "unavailable" in resp.json()["detail"].lower()

    def test_borrow_nonexistent_member_returns_404(self, client, make_book):
        book = make_book()
        resp = client.post("/api/v1/loans/borrow", json={
            "member_id": str(uuid.uuid4()),
            "book_id": str(book.id),
        })
        assert resp.status_code == 404

    def test_borrow_nonexistent_book_returns_404(self, client, make_member):
        member = make_member()
        resp = client.post("/api/v1/loans/borrow", json={
            "member_id": str(member.id),
            "book_id": str(uuid.uuid4()),
        })
        assert resp.status_code == 404

    def test_borrow_past_due_date_returns_422(self, client, make_book, make_member):
        book = make_book()
        member = make_member()
        past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        resp = client.post("/api/v1/loans/borrow", json={
            "member_id": str(member.id),
            "book_id": str(book.id),
            "due_at": past,
        })
        assert resp.status_code == 422  # Pydantic validation error

    def test_borrow_missing_fields_returns_422(self, client):
        resp = client.post("/api/v1/loans/borrow", json={"member_id": str(uuid.uuid4())})
        assert resp.status_code == 422


class TestReturnBook:
    def test_return_success(self, client, make_book, make_member, make_loan, db):
        book = make_book(copies_total=1, copies_available=0)
        member = make_member()
        loan = make_loan(member=member, book=book)

        resp = client.post("/api/v1/loans/return", json={"loan_id": str(loan.id)})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "RETURNED"
        assert data["returned_at"] is not None

    def test_return_increments_copies_available(self, client, make_book, make_member, make_loan, db):
        book = make_book(copies_total=1, copies_available=0)
        member = make_member()
        loan = make_loan(member=member, book=book)
        client.post("/api/v1/loans/return", json={"loan_id": str(loan.id)})
        db.refresh(book)
        assert book.copies_available == 1

    def test_return_overdue_book_calculates_fine(self, client, make_book, make_member, make_loan, db):
        book = make_book(copies_available=0)
        member = make_member()
        past_due = datetime.now(timezone.utc) - timedelta(days=5)
        loan = make_loan(member=member, book=book, due_at=past_due)

        resp = client.post("/api/v1/loans/return", json={"loan_id": str(loan.id)})
        assert resp.status_code == 200
        data = resp.json()
        assert float(data["fine_amount"]) >= 2.50  # ≥ 5 days × $0.50

    def test_return_already_returned_returns_400(self, client, make_book, make_member, make_loan):
        from app.models.loan import LoanStatus
        book = make_book()
        member = make_member()
        loan = make_loan(member=member, book=book, status=LoanStatus.RETURNED)
        resp = client.post("/api/v1/loans/return", json={"loan_id": str(loan.id)})
        assert resp.status_code == 400

    def test_return_nonexistent_loan_returns_404(self, client):
        resp = client.post("/api/v1/loans/return", json={"loan_id": str(uuid.uuid4())})
        assert resp.status_code == 404


class TestListLoans:
    def test_list_all_loans(self, client, make_book, make_member, make_loan):
        book = make_book()
        member = make_member()
        make_loan(member=member, book=book)
        resp = client.get("/api/v1/loans")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        assert "items" in data

    def test_list_loans_filter_by_member(self, client, make_book, make_member, make_loan):
        book = make_book()
        member = make_member()
        make_loan(member=member, book=book)
        resp = client.get(f"/api/v1/loans?member_id={member.id}")
        assert resp.status_code == 200
        items = resp.json()["items"]
        for item in items:
            assert item["member_id"] == str(member.id)

    def test_list_loans_filter_by_status(self, client, make_book, make_member, make_loan):
        from app.models.loan import LoanStatus
        book = make_book()
        member = make_member()
        make_loan(member=member, book=book, status=LoanStatus.RETURNED)
        resp = client.get("/api/v1/loans?status=RETURNED")
        assert resp.status_code == 200
        items = resp.json()["items"]
        for item in items:
            assert item["status"] == "RETURNED"


class TestOverdueLoans:
    def test_overdue_endpoint_returns_overdue_loans(self, client, make_book, make_member, make_loan):
        book = make_book(copies_available=0)
        member = make_member()
        past_due = datetime.now(timezone.utc) - timedelta(days=3)
        make_loan(member=member, book=book, due_at=past_due)

        resp = client.get("/api/v1/loans/overdue")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        for loan in data:
            assert loan["status"] == "OVERDUE"
            assert float(loan["fine_amount"]) > 0

    def test_overdue_endpoint_empty_when_no_overdue(self, client):
        resp = client.get("/api/v1/loans/overdue")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestMemberLoans:
    def test_get_member_loans(self, client, make_book, make_member, make_loan):
        book = make_book()
        member = make_member()
        make_loan(member=member, book=book)
        resp = client.get(f"/api/v1/members/{member.id}/loans")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert any(item["member_id"] == str(member.id) for item in data)

    def test_get_member_loans_active_only(self, client, make_book, make_member, make_loan):
        from app.models.loan import LoanStatus
        book1 = make_book()
        book2 = make_book()
        member = make_member()
        make_loan(member=member, book=book1, status=LoanStatus.BORROWED)
        make_loan(member=member, book=book2, status=LoanStatus.RETURNED)

        resp = client.get(f"/api/v1/members/{member.id}/loans?active_only=true")
        assert resp.status_code == 200
        items = resp.json()
        assert all(i["status"] == "BORROWED" for i in items)

    def test_get_member_loans_nonexistent_member_returns_404(self, client):
        resp = client.get(f"/api/v1/members/{uuid.uuid4()}/loans")
        assert resp.status_code == 404


class TestFullBorrowReturnFlow:
    def test_full_borrow_and_return_flow(self, client, make_book, make_member, db):
        """End-to-end: borrow a book, verify availability, then return it."""
        book = make_book(copies_total=1)
        member = make_member()

        # Borrow
        borrow_resp = client.post("/api/v1/loans/borrow", json={
            "member_id": str(member.id),
            "book_id": str(book.id),
        })
        assert borrow_resp.status_code == 201
        loan_id = borrow_resp.json()["id"]

        # Book should now be unavailable
        db.refresh(book)
        assert book.copies_available == 0

        # Return
        return_resp = client.post("/api/v1/loans/return", json={"loan_id": loan_id})
        assert return_resp.status_code == 200
        assert return_resp.json()["status"] == "RETURNED"

        # Book should be available again
        db.refresh(book)
        assert book.copies_available == 1

    def test_cannot_borrow_same_book_twice_when_only_one_copy(self, client, make_book, make_member):
        book = make_book(copies_total=1)
        member1 = make_member()
        member2 = make_member()

        r1 = client.post("/api/v1/loans/borrow", json={
            "member_id": str(member1.id), "book_id": str(book.id)
        })
        assert r1.status_code == 201

        r2 = client.post("/api/v1/loans/borrow", json={
            "member_id": str(member2.id), "book_id": str(book.id)
        })
        assert r2.status_code == 409

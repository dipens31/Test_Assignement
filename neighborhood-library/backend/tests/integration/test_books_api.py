"""
Integration tests for /api/v1/books endpoints.
Uses a real test PostgreSQL database with transaction rollback isolation.
"""
import pytest


class TestCreateBook:
    def test_create_book_success(self, client):
        resp = client.post("/api/v1/books", json={
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "copies_total": 3,
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Clean Code"
        assert data["author"] == "Robert C. Martin"
        assert data["copies_total"] == 3
        assert data["copies_available"] == 3
        assert "id" in data

    def test_create_book_with_isbn(self, client):
        resp = client.post("/api/v1/books", json={
            "title": "The Pragmatic Programmer",
            "author": "David Thomas",
            "isbn": "978-0-13-595705-9",
            "published_year": 2019,
            "copies_total": 2,
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["isbn"] == "978-0-13-595705-9"
        assert data["published_year"] == 2019

    def test_create_book_duplicate_isbn_returns_409(self, client):
        client.post("/api/v1/books", json={
            "title": "Book A", "author": "Author A", "isbn": "dup-isbn-001"
        })
        resp = client.post("/api/v1/books", json={
            "title": "Book B", "author": "Author B", "isbn": "dup-isbn-001"
        })
        assert resp.status_code == 409

    def test_create_book_missing_title_returns_422(self, client):
        resp = client.post("/api/v1/books", json={"author": "Author"})
        assert resp.status_code == 422

    def test_create_book_missing_author_returns_422(self, client):
        resp = client.post("/api/v1/books", json={"title": "Title"})
        assert resp.status_code == 422

    def test_create_book_zero_copies_returns_422(self, client):
        resp = client.post("/api/v1/books", json={
            "title": "T", "author": "A", "copies_total": 0
        })
        assert resp.status_code == 422


class TestGetBook:
    def test_get_existing_book(self, client, make_book):
        book = make_book(title="Test Get Book")
        resp = client.get(f"/api/v1/books/{book.id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == str(book.id)

    def test_get_nonexistent_book_returns_404(self, client):
        import uuid
        resp = client.get(f"/api/v1/books/{uuid.uuid4()}")
        assert resp.status_code == 404

    def test_get_invalid_uuid_returns_422(self, client):
        resp = client.get("/api/v1/books/not-a-uuid")
        assert resp.status_code == 422


class TestListBooks:
    def test_list_books_returns_paginated(self, client, make_book):
        make_book(title="Alpha Book")
        make_book(title="Beta Book")
        resp = client.get("/api/v1/books")
        assert resp.status_code == 200
        data = resp.json()
        assert "total" in data
        assert "items" in data
        assert len(data["items"]) >= 2

    def test_list_books_filter_by_title(self, client, make_book):
        make_book(title="Unique Title XYZ999")
        resp = client.get("/api/v1/books?title=XYZ999")
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert all("XYZ999" in item["title"] for item in items)

    def test_list_books_filter_by_author(self, client, make_book):
        make_book(author="UniqueAuthorABC")
        resp = client.get("/api/v1/books?author=UniqueAuthorABC")
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert all("UniqueAuthorABC" in item["author"] for item in items)

    def test_list_books_available_only(self, client, make_book):
        make_book(title="Available Book", copies_total=3, copies_available=3)
        make_book(title="Unavailable Book", copies_total=1, copies_available=0)
        resp = client.get("/api/v1/books?available_only=true")
        assert resp.status_code == 200
        items = resp.json()["items"]
        for item in items:
            assert item["copies_available"] > 0

    def test_list_books_pagination(self, client, make_book):
        for i in range(5):
            make_book(title=f"Paging Book {i}")
        resp = client.get("/api/v1/books?skip=0&limit=2")
        assert resp.status_code == 200
        assert len(resp.json()["items"]) <= 2


class TestUpdateBook:
    def test_update_book_title(self, client, make_book):
        book = make_book(title="Old Title")
        resp = client.put(f"/api/v1/books/{book.id}", json={"title": "New Title"})
        assert resp.status_code == 200
        assert resp.json()["title"] == "New Title"

    def test_update_book_copies_total_increase(self, client, make_book):
        book = make_book(copies_total=2)
        resp = client.put(f"/api/v1/books/{book.id}", json={"copies_total": 5})
        assert resp.status_code == 200
        data = resp.json()
        assert data["copies_total"] == 5
        assert data["copies_available"] == 5  # was 2, diff=+3

    def test_update_nonexistent_book_returns_404(self, client):
        import uuid
        resp = client.put(f"/api/v1/books/{uuid.uuid4()}", json={"title": "X"})
        assert resp.status_code == 404

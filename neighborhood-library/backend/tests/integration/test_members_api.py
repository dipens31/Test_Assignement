"""
Integration tests for /api/v1/members endpoints.
"""
import uuid

import pytest


class TestCreateMember:
    def test_create_member_success(self, client):
        resp = client.post("/api/v1/members", json={
            "name": "Alice Johnson",
            "email": "alice.johnson@example.com",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Alice Johnson"
        assert data["email"] == "alice.johnson@example.com"
        assert "id" in data

    def test_create_member_with_all_fields(self, client):
        resp = client.post("/api/v1/members", json={
            "name": "Bob Smith",
            "email": "bob.smith@example.com",
            "phone": "+1-555-0101",
            "address": "456 Elm Street",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["phone"] == "+1-555-0101"
        assert data["address"] == "456 Elm Street"

    def test_create_member_duplicate_email_returns_409(self, client):
        client.post("/api/v1/members", json={
            "name": "Carol", "email": "dup_test@example.com"
        })
        resp = client.post("/api/v1/members", json={
            "name": "Dave", "email": "dup_test@example.com"
        })
        assert resp.status_code == 409

    def test_create_member_invalid_email_returns_422(self, client):
        resp = client.post("/api/v1/members", json={
            "name": "Eve", "email": "not-an-email"
        })
        assert resp.status_code == 422

    def test_create_member_missing_name_returns_422(self, client):
        resp = client.post("/api/v1/members", json={"email": "a@example.com"})
        assert resp.status_code == 422

    def test_create_member_missing_email_returns_422(self, client):
        resp = client.post("/api/v1/members", json={"name": "Frank"})
        assert resp.status_code == 422


class TestGetMember:
    def test_get_existing_member(self, client, make_member):
        member = make_member(name="Grace")
        resp = client.get(f"/api/v1/members/{member.id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Grace"

    def test_get_nonexistent_member_returns_404(self, client):
        resp = client.get(f"/api/v1/members/{uuid.uuid4()}")
        assert resp.status_code == 404


class TestListMembers:
    def test_list_members(self, client, make_member):
        make_member(name="Henry")
        resp = client.get("/api/v1/members")
        assert resp.status_code == 200
        data = resp.json()
        assert "total" in data and "items" in data

    def test_list_members_filter_by_name(self, client, make_member):
        make_member(name="UniqueName_XYZ999")
        resp = client.get("/api/v1/members?name=XYZ999")
        items = resp.json()["items"]
        assert all("XYZ999" in i["name"] for i in items)


class TestUpdateMember:
    def test_update_member_name(self, client, make_member):
        member = make_member(name="Original Name")
        resp = client.put(f"/api/v1/members/{member.id}", json={"name": "Updated Name"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated Name"

    def test_update_member_phone(self, client, make_member):
        member = make_member()
        resp = client.put(f"/api/v1/members/{member.id}", json={"phone": "+44-20-7946-0958"})
        assert resp.status_code == 200
        assert resp.json()["phone"] == "+44-20-7946-0958"

    def test_update_nonexistent_member_returns_404(self, client):
        resp = client.put(f"/api/v1/members/{uuid.uuid4()}", json={"name": "X"})
        assert resp.status_code == 404

import pytest


class TestAuth:
    def test_register_user(self, client):
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "name": "New User",
                "password": "password123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["name"] == "New User"
        assert "id" in data

    def test_register_duplicate_email(self, client, test_user):
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "name": "Another User",
                "password": "password123"
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_login_success(self, client, test_user):
        response = client.post(
            "/api/auth/login",
            data={
                "username": "test@example.com",
                "password": "testpassword123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user):
        response = client.post(
            "/api/auth/login",
            data={
                "username": "test@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        response = client.post(
            "/api/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 401

    def test_get_current_user(self, client, auth_headers):
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"

    def test_get_current_user_unauthorized(self, client):
        response = client.get("/api/auth/me")
        assert response.status_code == 401

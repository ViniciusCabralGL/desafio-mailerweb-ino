import pytest


class TestRooms:
    def test_create_room(self, client, auth_headers):
        response = client.post(
            "/api/rooms/",
            json={
                "name": "Nova Sala",
                "capacity": 15,
                "description": "Sala para reuniões grandes"
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Nova Sala"
        assert data["capacity"] == 15

    def test_create_room_unauthorized(self, client):
        response = client.post(
            "/api/rooms/",
            json={
                "name": "Nova Sala",
                "capacity": 15
            }
        )
        assert response.status_code == 401

    def test_create_room_duplicate_name(self, client, auth_headers, test_room):
        response = client.post(
            "/api/rooms/",
            json={
                "name": "Sala de Reuniões 1",
                "capacity": 5
            },
            headers=auth_headers
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_room_invalid_capacity(self, client, auth_headers):
        response = client.post(
            "/api/rooms/",
            json={
                "name": "Nova Sala",
                "capacity": 0
            },
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_list_rooms(self, client, test_room):
        response = client.get("/api/rooms/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_get_room(self, client, test_room):
        response = client.get(f"/api/rooms/{test_room.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == test_room.name

    def test_get_room_not_found(self, client):
        response = client.get("/api/rooms/9999")
        assert response.status_code == 404

    def test_update_room(self, client, auth_headers, test_room):
        response = client.put(
            f"/api/rooms/{test_room.id}",
            json={
                "name": "Sala Atualizada",
                "capacity": 20
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Sala Atualizada"
        assert data["capacity"] == 20

    def test_delete_room(self, client, auth_headers, test_room):
        response = client.delete(
            f"/api/rooms/{test_room.id}",
            headers=auth_headers
        )
        assert response.status_code == 204

        # Verify deleted
        response = client.get(f"/api/rooms/{test_room.id}")
        assert response.status_code == 404

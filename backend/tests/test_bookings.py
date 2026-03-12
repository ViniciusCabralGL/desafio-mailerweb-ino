import pytest
from datetime import datetime, timedelta, timezone


class TestBookingValidation:
    """Test booking validation rules."""

    def test_create_booking_success(self, client, auth_headers, test_room):
        start = datetime.now(timezone.utc) + timedelta(hours=1)
        end = start + timedelta(hours=1)

        response = client.post(
            "/api/bookings/",
            json={
                "title": "Reunião de Planejamento",
                "room_id": test_room.id,
                "start_at": start.isoformat(),
                "end_at": end.isoformat(),
                "participants": [{"email": "participant@example.com"}]
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Reunião de Planejamento"
        assert data["status"] == "active"

    def test_create_booking_start_after_end(self, client, auth_headers, test_room):
        """Test that start_at must be before end_at."""
        start = datetime.now(timezone.utc) + timedelta(hours=2)
        end = start - timedelta(hours=1)

        response = client.post(
            "/api/bookings/",
            json={
                "title": "Invalid Booking",
                "room_id": test_room.id,
                "start_at": start.isoformat(),
                "end_at": end.isoformat()
            },
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_create_booking_duration_too_short(self, client, auth_headers, test_room):
        """Test minimum duration of 15 minutes."""
        start = datetime.now(timezone.utc) + timedelta(hours=1)
        end = start + timedelta(minutes=10)

        response = client.post(
            "/api/bookings/",
            json={
                "title": "Short Booking",
                "room_id": test_room.id,
                "start_at": start.isoformat(),
                "end_at": end.isoformat()
            },
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_create_booking_duration_too_long(self, client, auth_headers, test_room):
        """Test maximum duration of 8 hours."""
        start = datetime.now(timezone.utc) + timedelta(hours=1)
        end = start + timedelta(hours=9)

        response = client.post(
            "/api/bookings/",
            json={
                "title": "Long Booking",
                "room_id": test_room.id,
                "start_at": start.isoformat(),
                "end_at": end.isoformat()
            },
            headers=auth_headers
        )
        assert response.status_code == 422


class TestBookingConflicts:
    """Test booking conflict detection."""

    def test_create_conflicting_booking(self, client, auth_headers, test_room):
        """Test that overlapping bookings are rejected."""
        start = datetime.now(timezone.utc) + timedelta(hours=1)
        end = start + timedelta(hours=2)

        # Create first booking
        response = client.post(
            "/api/bookings/",
            json={
                "title": "First Meeting",
                "room_id": test_room.id,
                "start_at": start.isoformat(),
                "end_at": end.isoformat()
            },
            headers=auth_headers
        )
        assert response.status_code == 201

        # Try to create overlapping booking
        overlap_start = start + timedelta(minutes=30)
        overlap_end = end + timedelta(minutes=30)

        response = client.post(
            "/api/bookings/",
            json={
                "title": "Conflicting Meeting",
                "room_id": test_room.id,
                "start_at": overlap_start.isoformat(),
                "end_at": overlap_end.isoformat()
            },
            headers=auth_headers
        )
        assert response.status_code == 409
        assert "conflict" in response.json()["detail"].lower()

    def test_adjacent_bookings_allowed(self, client, auth_headers, test_room):
        """Test that touching bookings (end == start) are allowed."""
        start1 = datetime.now(timezone.utc) + timedelta(hours=1)
        end1 = start1 + timedelta(hours=1)

        # Create first booking
        response = client.post(
            "/api/bookings/",
            json={
                "title": "First Meeting",
                "room_id": test_room.id,
                "start_at": start1.isoformat(),
                "end_at": end1.isoformat()
            },
            headers=auth_headers
        )
        assert response.status_code == 201

        # Create adjacent booking (starts exactly when first ends)
        start2 = end1
        end2 = start2 + timedelta(hours=1)

        response = client.post(
            "/api/bookings/",
            json={
                "title": "Second Meeting",
                "room_id": test_room.id,
                "start_at": start2.isoformat(),
                "end_at": end2.isoformat()
            },
            headers=auth_headers
        )
        assert response.status_code == 201

    def test_canceled_booking_no_conflict(self, client, auth_headers, test_room):
        """Test that canceled bookings don't cause conflicts."""
        start = datetime.now(timezone.utc) + timedelta(hours=1)
        end = start + timedelta(hours=1)

        # Create and cancel first booking
        response = client.post(
            "/api/bookings/",
            json={
                "title": "First Meeting",
                "room_id": test_room.id,
                "start_at": start.isoformat(),
                "end_at": end.isoformat()
            },
            headers=auth_headers
        )
        booking_id = response.json()["id"]

        response = client.post(
            f"/api/bookings/{booking_id}/cancel",
            headers=auth_headers
        )
        assert response.status_code == 200

        # Create booking at same time should succeed
        response = client.post(
            "/api/bookings/",
            json={
                "title": "New Meeting",
                "room_id": test_room.id,
                "start_at": start.isoformat(),
                "end_at": end.isoformat()
            },
            headers=auth_headers
        )
        assert response.status_code == 201


class TestBookingPermissions:
    """Test booking permissions."""

    def test_cancel_own_booking(self, client, auth_headers, test_room):
        start = datetime.now(timezone.utc) + timedelta(hours=1)
        end = start + timedelta(hours=1)

        # Create booking
        response = client.post(
            "/api/bookings/",
            json={
                "title": "My Meeting",
                "room_id": test_room.id,
                "start_at": start.isoformat(),
                "end_at": end.isoformat()
            },
            headers=auth_headers
        )
        booking_id = response.json()["id"]

        # Cancel
        response = client.post(
            f"/api/bookings/{booking_id}/cancel",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["status"] == "canceled"

    def test_cannot_modify_canceled_booking(self, client, auth_headers, test_room):
        start = datetime.now(timezone.utc) + timedelta(hours=1)
        end = start + timedelta(hours=1)

        # Create and cancel booking
        response = client.post(
            "/api/bookings/",
            json={
                "title": "Meeting",
                "room_id": test_room.id,
                "start_at": start.isoformat(),
                "end_at": end.isoformat()
            },
            headers=auth_headers
        )
        booking_id = response.json()["id"]

        client.post(f"/api/bookings/{booking_id}/cancel", headers=auth_headers)

        # Try to update
        response = client.put(
            f"/api/bookings/{booking_id}",
            json={"title": "Updated Title"},
            headers=auth_headers
        )
        assert response.status_code == 400


class TestBookingOutbox:
    """Test that outbox events are created."""

    def test_booking_creates_outbox_event(self, client, auth_headers, test_room, db):
        from app.models.outbox import OutboxEvent, EventType

        start = datetime.now(timezone.utc) + timedelta(hours=1)
        end = start + timedelta(hours=1)

        response = client.post(
            "/api/bookings/",
            json={
                "title": "Meeting with Event",
                "room_id": test_room.id,
                "start_at": start.isoformat(),
                "end_at": end.isoformat()
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        booking_id = response.json()["id"]

        # Check outbox event was created
        event = db.query(OutboxEvent).filter(
            OutboxEvent.aggregate_id == booking_id,
            OutboxEvent.event_type == EventType.BOOKING_CREATED
        ).first()

        assert event is not None
        assert event.status.value == "pending"

    def test_cancel_creates_outbox_event(self, client, auth_headers, test_room, db):
        from app.models.outbox import OutboxEvent, EventType

        start = datetime.now(timezone.utc) + timedelta(hours=1)
        end = start + timedelta(hours=1)

        # Create booking
        response = client.post(
            "/api/bookings/",
            json={
                "title": "Meeting",
                "room_id": test_room.id,
                "start_at": start.isoformat(),
                "end_at": end.isoformat()
            },
            headers=auth_headers
        )
        booking_id = response.json()["id"]

        # Cancel booking
        client.post(f"/api/bookings/{booking_id}/cancel", headers=auth_headers)

        # Check outbox event was created
        event = db.query(OutboxEvent).filter(
            OutboxEvent.aggregate_id == booking_id,
            OutboxEvent.event_type == EventType.BOOKING_CANCELED
        ).first()

        assert event is not None

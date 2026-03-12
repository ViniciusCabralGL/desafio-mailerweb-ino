import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from app.models.outbox import OutboxEvent, EventType, EventStatus
from app.services.outbox_service import OutboxService
from app.services.email_service import EmailService


class TestOutboxService:
    def test_get_pending_events(self, db):
        # Create pending events
        for i in range(3):
            event = OutboxEvent(
                event_type=EventType.BOOKING_CREATED,
                aggregate_id=i + 1,
                idempotency_key=f"test_key_{i}",
                status=EventStatus.PENDING
            )
            event.set_payload({"test": f"data_{i}"})
            db.add(event)
        db.commit()

        service = OutboxService(db)
        events = service.get_pending_events(batch_size=10)

        assert len(events) == 3

    def test_get_pending_events_respects_retry_limit(self, db):
        # Create event that exceeded retry limit
        event = OutboxEvent(
            event_type=EventType.BOOKING_CREATED,
            aggregate_id=1,
            idempotency_key="exceeded_retry",
            status=EventStatus.FAILED,
            retry_count=10  # Exceeds default limit of 3
        )
        event.set_payload({"test": "data"})
        db.add(event)
        db.commit()

        service = OutboxService(db)
        events = service.get_pending_events()

        assert len(events) == 0

    def test_mark_completed(self, db):
        event = OutboxEvent(
            event_type=EventType.BOOKING_CREATED,
            aggregate_id=1,
            idempotency_key="test_complete",
            status=EventStatus.PENDING
        )
        event.set_payload({"test": "data"})
        db.add(event)
        db.commit()

        service = OutboxService(db)
        service.mark_completed(event)

        db.refresh(event)
        assert event.status == EventStatus.COMPLETED
        assert event.processed_at is not None

    def test_mark_failed(self, db):
        event = OutboxEvent(
            event_type=EventType.BOOKING_CREATED,
            aggregate_id=1,
            idempotency_key="test_fail",
            status=EventStatus.PENDING,
            retry_count=0
        )
        event.set_payload({"test": "data"})
        db.add(event)
        db.commit()

        service = OutboxService(db)
        service.mark_failed(event, "Test error")

        db.refresh(event)
        assert event.status == EventStatus.FAILED
        assert event.retry_count == 1
        assert event.error_message == "Test error"

    def test_idempotency_check(self, db):
        # Create completed event
        event = OutboxEvent(
            event_type=EventType.BOOKING_CREATED,
            aggregate_id=1,
            idempotency_key="idempotent_key",
            status=EventStatus.COMPLETED
        )
        event.set_payload({"test": "data"})
        db.add(event)
        db.commit()

        service = OutboxService(db)

        # Should return True for already processed
        assert service.check_idempotency("idempotent_key") is True

        # Should return False for new key
        assert service.check_idempotency("new_key") is False


class TestEmailService:
    def test_create_email_content(self):
        payload = {
            "event_type": "BOOKING_CREATED",
            "title": "Team Meeting",
            "room_name": "Conference Room A",
            "start_at": "2024-01-15T10:00:00",
            "end_at": "2024-01-15T11:00:00",
            "owner_name": "John Doe"
        }

        content = EmailService._create_email_content(payload)

        assert "Team Meeting" in content
        assert "Conference Room A" in content
        assert "Nova Reserva Criada" in content

    def test_get_subject_created(self):
        payload = {
            "event_type": "BOOKING_CREATED",
            "title": "Team Meeting"
        }

        subject = EmailService._get_subject(payload)
        assert "Nova Reserva" in subject
        assert "Team Meeting" in subject

    def test_get_subject_canceled(self):
        payload = {
            "event_type": "BOOKING_CANCELED",
            "title": "Team Meeting"
        }

        subject = EmailService._get_subject(payload)
        assert "Cancelada" in subject

    @patch('aiosmtplib.send')
    def test_send_notification_email_sync(self, mock_send):
        mock_send.return_value = None

        payload = {
            "event_type": "BOOKING_CREATED",
            "title": "Test Meeting",
            "room_name": "Room A",
            "start_at": "2024-01-15T10:00:00",
            "end_at": "2024-01-15T11:00:00",
            "owner_email": "owner@example.com",
            "owner_name": "Owner",
            "participant_emails": ["participant@example.com"]
        }

        result = EmailService.send_notification_email_sync(payload)

        assert result is True
        mock_send.assert_called_once()

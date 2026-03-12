from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from typing import List

from app.models.outbox import OutboxEvent, EventStatus
from app.core.config import settings


class OutboxService:
    def __init__(self, db: Session):
        self.db = db

    def get_pending_events(self, batch_size: int = None) -> List[OutboxEvent]:
        """
        Get pending events that haven't exceeded retry limit.
        Uses SELECT FOR UPDATE SKIP LOCKED to prevent multiple workers
        from processing the same events.
        """
        if batch_size is None:
            batch_size = settings.OUTBOX_BATCH_SIZE

        events = (
            self.db.query(OutboxEvent)
            .filter(
                and_(
                    OutboxEvent.status.in_([EventStatus.PENDING, EventStatus.FAILED]),
                    OutboxEvent.retry_count < settings.OUTBOX_RETRY_LIMIT
                )
            )
            .order_by(OutboxEvent.created_at)
            .limit(batch_size)
            .with_for_update(skip_locked=True)
            .all()
        )

        return events

    def mark_processing(self, event: OutboxEvent):
        """Mark event as processing."""
        event.status = EventStatus.PROCESSING
        self.db.commit()

    def mark_completed(self, event: OutboxEvent):
        """Mark event as successfully processed."""
        event.status = EventStatus.COMPLETED
        event.processed_at = datetime.utcnow()
        self.db.commit()

    def mark_failed(self, event: OutboxEvent, error_message: str):
        """Mark event as failed and increment retry count."""
        event.status = EventStatus.FAILED
        event.retry_count += 1
        event.error_message = error_message
        self.db.commit()

    def check_idempotency(self, idempotency_key: str) -> bool:
        """
        Check if an event with this idempotency key was already processed.
        Returns True if already processed (should skip).
        """
        event = (
            self.db.query(OutboxEvent)
            .filter(
                and_(
                    OutboxEvent.idempotency_key == idempotency_key,
                    OutboxEvent.status == EventStatus.COMPLETED
                )
            )
            .first()
        )
        return event is not None

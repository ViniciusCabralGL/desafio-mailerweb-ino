import logging
from app.workers.celery_app import celery_app
from app.core.database import SessionLocal
from app.services.outbox_service import OutboxService
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def process_outbox_events(self):
    """
    Process pending outbox events and send email notifications.
    This task is designed to be run periodically (e.g., every 10 seconds).
    """
    db = SessionLocal()
    try:
        outbox_service = OutboxService(db)
        events = outbox_service.get_pending_events()

        if not events:
            logger.debug("No pending events to process")
            return {"processed": 0}

        processed_count = 0
        for event in events:
            try:
                # Mark as processing
                outbox_service.mark_processing(event)

                # Check idempotency
                if outbox_service.check_idempotency(event.idempotency_key):
                    logger.info(f"Event {event.id} already processed (idempotency check)")
                    outbox_service.mark_completed(event)
                    continue

                # Get payload and send email
                payload = event.get_payload()
                EmailService.send_notification_email_sync(payload)

                # Mark as completed
                outbox_service.mark_completed(event)
                processed_count += 1
                logger.info(f"Successfully processed event {event.id}")

            except Exception as e:
                logger.error(f"Failed to process event {event.id}: {str(e)}")
                outbox_service.mark_failed(event, str(e))

        return {"processed": processed_count}

    finally:
        db.close()


@celery_app.task
def send_single_notification(event_id: int):
    """Send notification for a specific event."""
    db = SessionLocal()
    try:
        from app.models.outbox import OutboxEvent

        event = db.query(OutboxEvent).filter(OutboxEvent.id == event_id).first()
        if not event:
            logger.warning(f"Event {event_id} not found")
            return False

        outbox_service = OutboxService(db)

        try:
            outbox_service.mark_processing(event)
            payload = event.get_payload()
            EmailService.send_notification_email_sync(payload)
            outbox_service.mark_completed(event)
            return True
        except Exception as e:
            logger.error(f"Failed to send notification for event {event_id}: {str(e)}")
            outbox_service.mark_failed(event, str(e))
            return False

    finally:
        db.close()

"""
Simple worker that doesn't require Redis/Celery.
Runs as a standalone process polling the outbox table.
"""
import time
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.core.database import SessionLocal
from app.core.config import settings
from app.services.outbox_service import OutboxService
from app.services.email_service import EmailService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def process_events():
    """Process pending outbox events."""
    db = SessionLocal()
    try:
        outbox_service = OutboxService(db)
        events = outbox_service.get_pending_events()

        if not events:
            return 0

        processed_count = 0
        for event in events:
            try:
                logger.info(f"Processing event {event.id} ({event.event_type.value})")

                # Mark as processing
                outbox_service.mark_processing(event)

                # Check idempotency
                if outbox_service.check_idempotency(event.idempotency_key):
                    logger.info(f"Event {event.id} already processed (idempotency)")
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

        return processed_count

    finally:
        db.close()


def run_worker(poll_interval: int = 5):
    """
    Run the worker loop.

    Args:
        poll_interval: Seconds between polling for new events
    """
    logger.info(f"Starting outbox worker (poll interval: {poll_interval}s)")
    logger.info(f"Retry limit: {settings.OUTBOX_RETRY_LIMIT}")
    logger.info(f"Batch size: {settings.OUTBOX_BATCH_SIZE}")

    while True:
        try:
            processed = process_events()
            if processed > 0:
                logger.info(f"Processed {processed} events")
        except Exception as e:
            logger.error(f"Worker error: {str(e)}")

        time.sleep(poll_interval)


if __name__ == "__main__":
    run_worker()

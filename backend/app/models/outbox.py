from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum
from datetime import datetime
import enum
import json

from app.core.database import Base


class EventType(str, enum.Enum):
    BOOKING_CREATED = "BOOKING_CREATED"
    BOOKING_UPDATED = "BOOKING_UPDATED"
    BOOKING_CANCELED = "BOOKING_CANCELED"


class EventStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(SQLEnum(EventType), nullable=False)
    aggregate_id = Column(Integer, nullable=False, index=True)  # booking_id
    aggregate_type = Column(String(50), default="booking")
    payload = Column(Text, nullable=False)
    status = Column(SQLEnum(EventStatus), default=EventStatus.PENDING, index=True)
    retry_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    idempotency_key = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

    def set_payload(self, data: dict):
        self.payload = json.dumps(data)

    def get_payload(self) -> dict:
        return json.loads(self.payload)

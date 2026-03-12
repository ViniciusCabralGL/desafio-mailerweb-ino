from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
from typing import List, Optional
import uuid

from app.models.booking import Booking, BookingStatus, BookingParticipant
from app.models.room import Room
from app.models.user import User
from app.models.outbox import OutboxEvent, EventType, EventStatus
from app.schemas.booking import BookingCreate, BookingUpdate


class BookingService:
    def __init__(self, db: Session):
        self.db = db

    def check_conflict(
        self,
        room_id: int,
        start_at,
        end_at,
        exclude_booking_id: Optional[int] = None
    ) -> bool:
        """
        Check if there's a conflict with existing active bookings.
        Conflict detection: new_start < existing_end AND new_end > existing_start
        Touching times (end == start) are allowed.
        """
        query = self.db.query(Booking).filter(
            Booking.room_id == room_id,
            Booking.status == BookingStatus.ACTIVE,
            Booking.start_at < end_at,
            Booking.end_at > start_at
        )

        if exclude_booking_id:
            query = query.filter(Booking.id != exclude_booking_id)

        return query.first() is not None

    def create_booking(self, booking_data: BookingCreate, owner: User) -> Booking:
        """
        Create a booking with conflict detection and outbox event.
        Uses database-level locking to prevent race conditions.
        """
        # Verify room exists
        room = self.db.query(Room).filter(Room.id == booking_data.room_id).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found"
            )

        # Lock the room row to prevent concurrent conflicting bookings
        # This uses SELECT FOR UPDATE to acquire an exclusive lock
        self.db.query(Room).filter(Room.id == booking_data.room_id).with_for_update().first()

        # Check for conflicts
        if self.check_conflict(booking_data.room_id, booking_data.start_at, booking_data.end_at):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Booking conflicts with an existing reservation"
            )

        # Create booking
        booking = Booking(
            title=booking_data.title,
            room_id=booking_data.room_id,
            owner_id=owner.id,
            start_at=booking_data.start_at,
            end_at=booking_data.end_at,
            status=BookingStatus.ACTIVE
        )
        self.db.add(booking)
        self.db.flush()  # Get the booking ID

        # Add participants
        for participant in booking_data.participants:
            # Check if participant is a registered user
            user = self.db.query(User).filter(User.email == participant.email).first()
            bp = BookingParticipant(
                booking_id=booking.id,
                email=participant.email,
                user_id=user.id if user else None
            )
            self.db.add(bp)

        # Create outbox event (same transaction)
        self._create_outbox_event(booking, EventType.BOOKING_CREATED, room)

        self.db.commit()
        self.db.refresh(booking)
        return booking

    def update_booking(
        self,
        booking_id: int,
        booking_data: BookingUpdate,
        current_user: User
    ) -> Booking:
        """Update a booking with conflict detection and outbox event."""
        booking = self.db.query(Booking).filter(Booking.id == booking_id).first()

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )

        if booking.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this booking"
            )

        if booking.status == BookingStatus.CANCELED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify a canceled booking"
            )

        # Determine the room_id and times to check
        room_id = booking_data.room_id if booking_data.room_id else booking.room_id
        start_at = booking_data.start_at if booking_data.start_at else booking.start_at
        end_at = booking_data.end_at if booking_data.end_at else booking.end_at

        # Lock the room
        self.db.query(Room).filter(Room.id == room_id).with_for_update().first()

        # Check conflicts (excluding current booking)
        if self.check_conflict(room_id, start_at, end_at, exclude_booking_id=booking_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Booking conflicts with an existing reservation"
            )

        # Update fields
        if booking_data.title is not None:
            booking.title = booking_data.title
        if booking_data.room_id is not None:
            booking.room_id = booking_data.room_id
        if booking_data.start_at is not None:
            booking.start_at = booking_data.start_at
        if booking_data.end_at is not None:
            booking.end_at = booking_data.end_at

        # Update participants if provided
        if booking_data.participants is not None:
            # Remove existing participants
            self.db.query(BookingParticipant).filter(
                BookingParticipant.booking_id == booking_id
            ).delete()

            # Add new participants
            for participant in booking_data.participants:
                user = self.db.query(User).filter(User.email == participant.email).first()
                bp = BookingParticipant(
                    booking_id=booking.id,
                    email=participant.email,
                    user_id=user.id if user else None
                )
                self.db.add(bp)

        # Get room for outbox
        room = self.db.query(Room).filter(Room.id == booking.room_id).first()

        # Create outbox event
        self._create_outbox_event(booking, EventType.BOOKING_UPDATED, room)

        self.db.commit()
        self.db.refresh(booking)
        return booking

    def cancel_booking(self, booking_id: int, current_user: User) -> Booking:
        """Cancel a booking (soft delete) and create outbox event."""
        booking = self.db.query(Booking).filter(Booking.id == booking_id).first()

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )

        if booking.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to cancel this booking"
            )

        if booking.status == BookingStatus.CANCELED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Booking is already canceled"
            )

        booking.status = BookingStatus.CANCELED

        # Get room for outbox
        room = self.db.query(Room).filter(Room.id == booking.room_id).first()

        # Create outbox event
        self._create_outbox_event(booking, EventType.BOOKING_CANCELED, room)

        self.db.commit()
        self.db.refresh(booking)
        return booking

    def _create_outbox_event(self, booking: Booking, event_type: EventType, room: Room):
        """Create an outbox event in the same transaction."""
        # Generate idempotency key
        idempotency_key = f"{event_type.value}_{booking.id}_{booking.updated_at.isoformat()}"

        # Get participant emails
        participant_emails = [p.email for p in booking.participants]

        # Include owner email
        owner = self.db.query(User).filter(User.id == booking.owner_id).first()

        payload = {
            "booking_id": booking.id,
            "title": booking.title,
            "room_name": room.name,
            "start_at": booking.start_at.isoformat(),
            "end_at": booking.end_at.isoformat(),
            "status": booking.status.value,
            "owner_email": owner.email,
            "owner_name": owner.name,
            "participant_emails": participant_emails,
            "event_type": event_type.value
        }

        event = OutboxEvent(
            event_type=event_type,
            aggregate_id=booking.id,
            aggregate_type="booking",
            idempotency_key=idempotency_key,
            status=EventStatus.PENDING
        )
        event.set_payload(payload)
        self.db.add(event)

    def get_booking(self, booking_id: int) -> Optional[Booking]:
        return self.db.query(Booking).filter(Booking.id == booking_id).first()

    def list_bookings(
        self,
        room_id: Optional[int] = None,
        status: Optional[BookingStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Booking]:
        query = self.db.query(Booking)

        if room_id:
            query = query.filter(Booking.room_id == room_id)
        if status:
            query = query.filter(Booking.status == status)

        return query.order_by(Booking.start_at.desc()).offset(skip).limit(limit).all()

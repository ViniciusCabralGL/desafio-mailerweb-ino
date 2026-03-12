from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.booking import Booking, BookingStatus
from app.models.user import User
from app.schemas.booking import (
    BookingCreate,
    BookingUpdate,
    BookingResponse,
    BookingListResponse
)
from app.services.booking_service import BookingService

router = APIRouter()


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new booking.

    - Validates time constraints (start < end, 15min-8h duration)
    - Checks for conflicts with existing active bookings
    - Creates outbox event for email notification
    """
    service = BookingService(db)
    return service.create_booking(booking_data, current_user)


@router.get("/", response_model=List[BookingListResponse])
def list_bookings(
    room_id: Optional[int] = Query(None, description="Filter by room ID"),
    status: Optional[BookingStatus] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List all bookings with optional filters."""
    service = BookingService(db)
    return service.list_bookings(room_id=room_id, status=status, skip=skip, limit=limit)


@router.get("/my", response_model=List[BookingListResponse])
def list_my_bookings(
    status: Optional[BookingStatus] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List bookings owned by the current user."""
    query = db.query(Booking).filter(Booking.owner_id == current_user.id)

    if status:
        query = query.filter(Booking.status == status)

    return query.order_by(Booking.start_at.desc()).offset(skip).limit(limit).all()


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    """Get a specific booking by ID."""
    service = BookingService(db)
    booking = service.get_booking(booking_id)

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    return booking


@router.put("/{booking_id}", response_model=BookingResponse)
def update_booking(
    booking_id: int,
    booking_data: BookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing booking.

    - Only the owner can update
    - Cannot update canceled bookings
    - Validates time constraints and conflicts
    - Creates outbox event for email notification
    """
    service = BookingService(db)
    return service.update_booking(booking_id, booking_data, current_user)


@router.post("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel a booking (soft delete).

    - Only the owner can cancel
    - Creates outbox event for email notification
    - Canceled bookings are never removed
    """
    service = BookingService(db)
    return service.cancel_booking(booking_id, current_user)

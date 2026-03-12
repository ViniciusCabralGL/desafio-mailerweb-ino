from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.room import Room
from app.models.user import User
from app.schemas.room import RoomCreate, RoomUpdate, RoomResponse

router = APIRouter()


@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(
    room_data: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new room."""
    # Check if room name already exists
    existing_room = db.query(Room).filter(Room.name == room_data.name).first()
    if existing_room:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room with this name already exists"
        )

    room = Room(**room_data.model_dump())
    db.add(room)
    db.commit()
    db.refresh(room)

    return room


@router.get("/", response_model=List[RoomResponse])
def list_rooms(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all rooms."""
    rooms = db.query(Room).order_by(Room.name).offset(skip).limit(limit).all()
    return rooms


@router.get("/{room_id}", response_model=RoomResponse)
def get_room(room_id: int, db: Session = Depends(get_db)):
    """Get a specific room by ID."""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    return room


@router.put("/{room_id}", response_model=RoomResponse)
def update_room(
    room_id: int,
    room_data: RoomUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a room."""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )

    # Check name uniqueness if updating name
    if room_data.name and room_data.name != room.name:
        existing = db.query(Room).filter(Room.name == room_data.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Room with this name already exists"
            )

    update_data = room_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(room, field, value)

    db.commit()
    db.refresh(room)
    return room


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a room."""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )

    db.delete(room)
    db.commit()

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class BookingStatus(str, enum.Enum):
    ACTIVE = "active"
    CANCELED = "canceled"


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_at = Column(DateTime(timezone=True), nullable=False, index=True)
    end_at = Column(DateTime(timezone=True), nullable=False, index=True)
    status = Column(SQLEnum(BookingStatus), default=BookingStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    room = relationship("Room", back_populates="bookings")
    owner = relationship("User", back_populates="bookings")
    participants = relationship("BookingParticipant", back_populates="booking", cascade="all, delete-orphan")


class BookingParticipant(Base):
    __tablename__ = "booking_participants"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    email = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    booking = relationship("Booking", back_populates="participants")
    user = relationship("User", back_populates="participations")

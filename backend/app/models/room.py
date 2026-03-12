from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    capacity = Column(Integer, nullable=False)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    bookings = relationship("Booking", back_populates="room")

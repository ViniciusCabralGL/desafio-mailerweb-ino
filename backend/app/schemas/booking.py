from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime
from typing import Optional, List
from app.models.booking import BookingStatus


class ParticipantCreate(BaseModel):
    email: str


class ParticipantResponse(BaseModel):
    id: int
    email: str
    user_id: Optional[int]

    class Config:
        from_attributes = True


class BookingCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    room_id: int
    start_at: datetime
    end_at: datetime
    participants: List[ParticipantCreate] = []

    @model_validator(mode='after')
    def validate_times(self):
        if self.start_at >= self.end_at:
            raise ValueError("start_at must be before end_at")

        duration = (self.end_at - self.start_at).total_seconds() / 60
        if duration < 15:
            raise ValueError("Booking duration must be at least 15 minutes")
        if duration > 480:  # 8 hours = 480 minutes
            raise ValueError("Booking duration cannot exceed 8 hours")

        return self


class BookingUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    room_id: Optional[int] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    participants: Optional[List[ParticipantCreate]] = None

    @model_validator(mode='after')
    def validate_times(self):
        if self.start_at is not None and self.end_at is not None:
            if self.start_at >= self.end_at:
                raise ValueError("start_at must be before end_at")

            duration = (self.end_at - self.start_at).total_seconds() / 60
            if duration < 15:
                raise ValueError("Booking duration must be at least 15 minutes")
            if duration > 480:
                raise ValueError("Booking duration cannot exceed 8 hours")

        return self


class BookingResponse(BaseModel):
    id: int
    title: str
    room_id: int
    owner_id: int
    start_at: datetime
    end_at: datetime
    status: BookingStatus
    participants: List[ParticipantResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookingListResponse(BaseModel):
    id: int
    title: str
    room_id: int
    owner_id: int
    start_at: datetime
    end_at: datetime
    status: BookingStatus
    created_at: datetime

    class Config:
        from_attributes = True

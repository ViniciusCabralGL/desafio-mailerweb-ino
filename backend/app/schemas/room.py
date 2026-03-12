from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class RoomCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    capacity: int = Field(..., gt=0)
    description: Optional[str] = Field(None, max_length=500)


class RoomUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    capacity: Optional[int] = Field(None, gt=0)
    description: Optional[str] = Field(None, max_length=500)


class RoomResponse(BaseModel):
    id: int
    name: str
    capacity: int
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

from fastapi import APIRouter
from app.api import auth, rooms, bookings

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(rooms.router, prefix="/rooms", tags=["Rooms"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])

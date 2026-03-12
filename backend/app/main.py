from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import settings
from app.core.database import engine, Base

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="API for room booking management with async email notifications",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "MailerWeb Room Booking API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}

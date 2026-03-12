from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "MailerWeb Room Booking"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/mailerweb"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Email
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "noreply@mailerweb.com"
    SMTP_FROM_NAME: str = "MailerWeb Booking"
    SMTP_TLS: bool = False

    # Worker
    OUTBOX_RETRY_LIMIT: int = 3
    OUTBOX_BATCH_SIZE: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

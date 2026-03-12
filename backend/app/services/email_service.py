import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    @staticmethod
    def _create_email_content(payload: dict) -> str:
        """Create HTML email content based on event type."""
        event_type = payload.get("event_type", "")
        title = payload.get("title", "")
        room_name = payload.get("room_name", "")
        start_at = payload.get("start_at", "")
        end_at = payload.get("end_at", "")
        owner_name = payload.get("owner_name", "")

        event_labels = {
            "BOOKING_CREATED": "Nova Reserva Criada",
            "BOOKING_UPDATED": "Reserva Atualizada",
            "BOOKING_CANCELED": "Reserva Cancelada"
        }

        event_label = event_labels.get(event_type, event_type)

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .detail {{ margin: 10px 0; }}
                .label {{ font-weight: bold; color: #555; }}
                .footer {{ text-align: center; padding: 20px; color: #777; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{event_label}</h1>
                </div>
                <div class="content">
                    <div class="detail">
                        <span class="label">Reunião:</span> {title}
                    </div>
                    <div class="detail">
                        <span class="label">Sala:</span> {room_name}
                    </div>
                    <div class="detail">
                        <span class="label">Início:</span> {start_at}
                    </div>
                    <div class="detail">
                        <span class="label">Término:</span> {end_at}
                    </div>
                    <div class="detail">
                        <span class="label">Organizador:</span> {owner_name}
                    </div>
                </div>
                <div class="footer">
                    <p>Este é um email automático do sistema de reservas MailerWeb.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html

    @staticmethod
    def _get_subject(payload: dict) -> str:
        """Generate email subject based on event type."""
        event_type = payload.get("event_type", "")
        title = payload.get("title", "Reserva")

        subjects = {
            "BOOKING_CREATED": f"Nova Reserva: {title}",
            "BOOKING_UPDATED": f"Reserva Atualizada: {title}",
            "BOOKING_CANCELED": f"Reserva Cancelada: {title}"
        }

        return subjects.get(event_type, f"Notificação de Reserva: {title}")

    @staticmethod
    async def send_notification_email(payload: dict) -> bool:
        """
        Send notification email to owner and all participants.
        Returns True if successful, raises exception on failure.
        """
        recipients = [payload.get("owner_email")]
        participants = payload.get("participant_emails", [])
        recipients.extend(participants)

        # Remove duplicates and None values
        recipients = list(set(filter(None, recipients)))

        if not recipients:
            logger.warning("No recipients for email notification")
            return True

        subject = EmailService._get_subject(payload)
        html_content = EmailService._create_email_content(payload)

        message = MIMEMultipart("alternative")
        message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        message["To"] = ", ".join(recipients)
        message["Subject"] = subject

        html_part = MIMEText(html_content, "html")
        message.attach(html_part)

        try:
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                use_tls=settings.SMTP_TLS
            )
            logger.info(f"Email sent successfully to {recipients}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            raise

    @staticmethod
    def send_notification_email_sync(payload: dict) -> bool:
        """Synchronous version for Celery worker."""
        import asyncio

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(EmailService.send_notification_email(payload))
        finally:
            loop.close()

from __future__ import annotations

import smtplib
from email.message import EmailMessage

from app.agent.lead_capture import LeadCaptureState
from app.config import settings


class LeadEmailNotifier:
    def send(self, lead: LeadCaptureState) -> None:
        if not settings.smtp_host:
            raise RuntimeError("SMTP_HOST is not configured")
        if not settings.smtp_from_email:
            raise RuntimeError("SMTP_FROM_EMAIL or SMTP_USERNAME is not configured")
        if settings.smtp_username and not settings.smtp_app_password:
            raise RuntimeError("SMTP_APP_PASSWORD is not configured")

        message = EmailMessage()
        message["Subject"] = f"Technical support lead: {lead.requested_item}"
        message["From"] = settings.smtp_from_email
        message["To"] = settings.lead_notification_email
        message.set_content(
            "A customer requested protected technical or commercial information.\n\n"
            f"Requested item: {lead.requested_item}\n"
            f"Original request: {lead.original_request}\n"
            f"Full Name: {lead.full_name}\n"
            f"Email Address: {lead.email}\n"
            f"Contact Number: {lead.contact_number}\n"
            f"Company Name: {lead.company_name}\n"
        )

        smtp_class = smtplib.SMTP_SSL if settings.smtp_use_ssl else smtplib.SMTP
        with smtp_class(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
            if settings.smtp_use_tls and not settings.smtp_use_ssl:
                smtp.starttls()
            if settings.smtp_username:
                smtp.login(settings.smtp_username, settings.smtp_app_password or "")
            smtp.send_message(message)

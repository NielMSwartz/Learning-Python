"""Minimal SMTP helper for password reset messages.

If SMTP is not configured the one-time reset link is returned to the requester
instead. That keeps a personal, self-hosted installation fully functional
without requiring an email provider.
"""

from __future__ import annotations

import smtplib
from email.message import EmailMessage

from flask import current_app, url_for


def send_password_reset(user, token: str) -> bool:
    server = current_app.config.get("MAIL_SERVER")
    if not server:
        return False
    link = f"{current_app.config['PUBLIC_BASE_URL']}/reset/{token}"
    message = EmailMessage()
    message["Subject"] = "Reset your Python Academy password"
    message["From"] = current_app.config["MAIL_DEFAULT_SENDER"]
    message["To"] = user.email
    message.set_content(
        f"Hi {user.username},\n\nUse this one-time link within 30 minutes to reset your password:\n\n"
        f"{link}\n\nIf you did not request this, you can ignore the message.\n"
    )
    with smtplib.SMTP(server, current_app.config["MAIL_PORT"], timeout=10) as smtp:
        if current_app.config["MAIL_USE_TLS"]:
            smtp.starttls()
        if current_app.config["MAIL_USERNAME"]:
            smtp.login(current_app.config["MAIL_USERNAME"], current_app.config["MAIL_PASSWORD"])
        smtp.send_message(message)
    return True

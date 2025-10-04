from __future__ import annotations

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Sequence


def send_email(subject: str, html_body: str) -> None:
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    mail_from = os.getenv("SMTP_FROM") or user
    to_raw = os.getenv("SMTP_TO", "")
    recipients = [addr.strip() for addr in to_raw.split(",") if addr.strip()]

    if not host or not recipients:
        return  # Email not configured; silently skip

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = mail_from
    msg["To"] = ", ".join(recipients)

    part = MIMEText(html_body, "html")
    msg.attach(part)

    # Prefer STARTTLS on 587; support implicit SSL on 465
    if port == 465:
        server = smtplib.SMTP_SSL(host, port)
    else:
        server = smtplib.SMTP(host, port)
        server.starttls()

    try:
        if user and password:
            server.login(user, password)
        server.sendmail(mail_from, recipients, msg.as_string())
    finally:
        server.quit()

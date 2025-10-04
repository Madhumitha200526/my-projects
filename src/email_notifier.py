import os
import smtplib
from email.message import EmailMessage
from typing import List

from .config import SETTINGS


def _bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y"}


def send_update_email(num_rows_appended: int, spreadsheet_path: str) -> None:
    if not SETTINGS.smtp_host or not SETTINGS.email_from or not SETTINGS.email_to:
        return  # Email not configured

    subject = f"Student spreadsheet updated: {num_rows_appended} new record(s)"
    body = (
        f"The student spreadsheet has been updated.\n\n"
        f"Records added: {num_rows_appended}\n"
        f"Spreadsheet: {spreadsheet_path}\n"
    )
    msg = EmailMessage()
    msg["From"] = SETTINGS.email_from
    msg["To"] = SETTINGS.email_to
    msg["Subject"] = subject
    msg.set_content(body)

    if SETTINGS.email_attach_spreadsheet and os.path.exists(spreadsheet_path):
        with open(spreadsheet_path, "rb") as f:
            data = f.read()
        msg.add_attachment(
            data,
            maintype="application",
            subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=os.path.basename(spreadsheet_path),
        )

    if SETTINGS.smtp_use_tls:
        with smtplib.SMTP(SETTINGS.smtp_host, SETTINGS.smtp_port) as server:
            server.starttls()
            if SETTINGS.smtp_username and SETTINGS.smtp_password:
                server.login(SETTINGS.smtp_username, SETTINGS.smtp_password)
            server.send_message(msg)
    else:
        with smtplib.SMTP(SETTINGS.smtp_host, SETTINGS.smtp_port) as server:
            if SETTINGS.smtp_username and SETTINGS.smtp_password:
                server.login(SETTINGS.smtp_username, SETTINGS.smtp_password)
            server.send_message(msg)

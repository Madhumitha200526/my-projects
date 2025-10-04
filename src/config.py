import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def _get_bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "y"}


@dataclass(frozen=True)
class Settings:
    students_root: str = os.getenv("STUDENTS_ROOT", os.path.join(os.getcwd(), "students"))
    spreadsheet_path: str = os.getenv("SPREADSHEET_PATH", os.path.join(os.getcwd(), "data", "student_report.xlsx"))
    state_path: str = os.getenv("STATE_PATH", os.path.join(os.getcwd(), "data", "state.json"))
    run_every_hours: int = int(os.getenv("RUN_EVERY_HOURS", "2"))
    tesseract_cmd: str = os.getenv("TESSERACT_CMD", "tesseract")

    smtp_host: str = os.getenv("SMTP_HOST", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_use_tls: bool = _get_bool("SMTP_USE_TLS", True)
    email_from: str = os.getenv("EMAIL_FROM", "")
    email_to: str = os.getenv("EMAIL_TO", "")
    email_attach_spreadsheet: bool = _get_bool("EMAIL_ATTACH_SPREADSHEET", False)


SETTINGS = Settings()

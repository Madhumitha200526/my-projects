import argparse
import sys
import time
from datetime import datetime
from typing import List

import schedule

from .config import SETTINGS
from .scanner import iter_student_images
from .ocr_engine import OCREngine
from .parser import parse_metrics
from .state_store import StateStore
from .excel_writer import ExcelWriter
from .email_notifier import send_update_email


def process_once() -> int:
    state = StateStore(SETTINGS.state_path)
    ocr = OCREngine()
    excel = ExcelWriter(SETTINGS.spreadsheet_path)

    rows_to_append: List[List[str]] = []

    for student_name, image_path in iter_student_images(SETTINGS.students_root):
        if state.is_processed(image_path, student_name):
            continue
        text = ocr.extract_text(image_path)
        if not text:
            state.mark_processed(image_path, student_name)
            continue
        metrics = parse_metrics(text)
        # Day number auto-increment per student
        day_number = state.get_next_day_number(student_name)

        row = [
            student_name,
            str(day_number),
            metrics.get("accuracy") or "",
            metrics.get("wpm") or "",
            metrics.get("ocr_snippet") or "",
            metrics.get("course_completed_level") or "",
            metrics.get("completed_level") or "",
            # Processed At and Image File are filled in ExcelWriter if missing
            # We'll still put the image file explicitly
            datetime.utcnow().isoformat() + "Z",
            image_path,
        ]
        rows_to_append.append(row)
        state.mark_processed(image_path, student_name)

    appended = 0
    if rows_to_append:
        appended = excel.append_rows(rows_to_append)
        state.update_last_run()
        state.save()
        send_update_email(appended, SETTINGS.spreadsheet_path)
    else:
        # Still update last run timestamp even if nothing appended
        state.update_last_run()
        state.save()

    return appended


def main() -> None:
    parser = argparse.ArgumentParser(description="Automate OCR to Excel updater")
    parser.add_argument("--run-once", action="store_true", help="Run a single processing pass and exit")
    args = parser.parse_args()

    if args.run_once:
        count = process_once()
        print(f"Processed and appended {count} new row(s)")
        return

    # Scheduler mode
    schedule.every(SETTINGS.run_every_hours).hours.do(process_once)
    print(f"Scheduler started. Running every {SETTINGS.run_every_hours} hour(s). Press Ctrl+C to stop.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(10)
    except KeyboardInterrupt:
        print("Stopped.")


if __name__ == "__main__":
    main()

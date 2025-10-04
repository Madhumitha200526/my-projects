from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime
from typing import Iterator, Tuple

from dotenv import load_dotenv

# Local modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from automation_ocr.ocr import perform_ocr
from automation_ocr.parser import parse_fields_from_text
from automation_ocr.excel_writer import append_row
from automation_ocr.notifier import send_email
from automation_ocr.state import ProcessedState


IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


def iter_images(root: str) -> Iterator[Tuple[str, float]]:
    for dirpath, _, filenames in os.walk(root):
        for name in sorted(filenames):
            ext = os.path.splitext(name)[1].lower()
            if ext in IMAGE_EXTS:
                path = os.path.join(dirpath, name)
                try:
                    stat = os.stat(path)
                    yield path, stat.st_mtime
                except FileNotFoundError:
                    continue


def main() -> int:
    load_dotenv()

    parser = argparse.ArgumentParser(description="OCR student screenshots and update Excel")
    parser.add_argument("--root", default=os.getenv("STUDENTS_ROOT", "students"), help="Root folder of student folders")
    parser.add_argument("--excel", default=os.getenv("OUTPUT_EXCEL", "outputs/progress.xlsx"), help="Output Excel file path")
    parser.add_argument("--state", default=os.getenv("STATE_FILE", "state/state.json"), help="State JSON file path")
    args = parser.parse_args()

    root = args.root
    excel_path = args.excel
    state_path = args.state

    os.makedirs(os.path.dirname(excel_path), exist_ok=True)
    os.makedirs(os.path.dirname(state_path), exist_ok=True)

    state = ProcessedState.load(state_path)

    new_rows = 0
    for image_path, mtime in iter_images(root):
        if not state.should_process(image_path, mtime):
            continue

        ocr_result = perform_ocr(image_path)
        fields = parse_fields_from_text(ocr_result.text, image_path)

        append_row(
            path=excel_path,
            student_name=fields.student_name,
            day=fields.day_number,
            accuracy=fields.accuracy_percent,
            wpm=fields.words_per_minute,
            course_level=fields.course_completed_level,
            completed_level=fields.completed_level,
            snippet=ocr_result.snippet,
            image_path=image_path,
            image_mtime=mtime,
        )
        state.mark_processed(image_path, mtime)
        new_rows += 1

    state.save(state_path)

    if new_rows > 0:
        prefix = os.getenv("EMAIL_SUBJECT_PREFIX", "[Student OCR]")
        subject = f"{prefix} Updated {new_rows} row(s) at {datetime.now().isoformat()}"
        excel_rel = os.path.relpath(excel_path)
        html = f"<p>Excel updated with <b>{new_rows}</b> new row(s).</p>" \
               f"<p>File: {excel_rel}</p>" \
               f"<p>Root scanned: {root}</p>"
        send_email(subject, html)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

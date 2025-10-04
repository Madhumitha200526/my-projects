## Student Screenshot OCR to Excel

This utility scans each student's folder for screenshots, performs OCR to extract key metrics, and appends results to an Excel spreadsheet. After updates, it sends an email notification.

### Features
- Automatically reads all screenshots under each student's folder
- Extracts: Student name, Day number, Accuracy (%), Words per minute (WPM), Course completed level, Completed level, OCR text snippet, and file info
- Appends results to an Excel file with headers
- Avoids duplicates using a state file keyed by file path and modified time
- Sends an email when new rows are added
- Designed to run every 2 hours via cron

### Requirements
- Linux with Python 3.9+
- Tesseract OCR engine installed system-wide
  - Debian/Ubuntu: `sudo apt-get update && sudo apt-get install -y tesseract-ocr`
- Python dependencies: `pip install -r requirements.txt`

### Configuration
Copy `.env.example` to `.env` and adjust values:

- `STUDENTS_ROOT`: Root directory containing subfolders per student (e.g., `students/John Doe/`)
- `OUTPUT_EXCEL`: Path to Excel file (will be created if missing)
- `STATE_FILE`: JSON file tracking processed images to avoid duplicates
- `TESSERACT_CMD`: Optional path to `tesseract` binary if not in PATH
- SMTP settings: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `SMTP_FROM`, `SMTP_TO`, `EMAIL_SUBJECT_PREFIX`

### Folder Structure
```
students/
  Alice/
    2025-10-01-screenshot1.png
  Bob/
    day2.jpg
```

### Run Once
```
python scripts/main.py --root students --excel outputs/progress.xlsx --state state/state.json
```

If environment variables are set in `.env`, you can omit flags:
```
python scripts/main.py
```

### Run Every 2 Hours (cron)
Edit crontab:
```
crontab -e
```
Add:
```
0 */2 * * * cd /workspace && /usr/bin/python3 scripts/main.py >> logs/cron.log 2>&1
```

### Notes on Parsing
The parser tries multiple patterns, e.g. `Accuracy: 97%`, `WPM: 45`, `Day 3`, `Completed Level: 5`, `Course Completed Level: 2/10`. If a field is missing, it may be left blank.

### Troubleshooting
- If OCR returns poor results, ensure Tesseract is installed and try higher-resolution screenshots.
- To point to a non-default tesseract path, set `TESSERACT_CMD` in `.env`.
- Email issues: verify SMTP credentials and port (587 with STARTTLS or 465 for SSL).

from __future__ import annotations

import os
import re
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any


@dataclass
class ParsedFields:
    student_name: str
    day_number: Optional[int]
    accuracy_percent: Optional[float]
    words_per_minute: Optional[int]
    course_completed_level: Optional[str]
    completed_level: Optional[str]

    @staticmethod
    def headers() -> list[str]:
        return [
            "Student Name",
            "Day",
            "Accuracy %",
            "WPM",
            "Course Completed Level",
            "Completed Level",
            "OCR Snippet",
            "Image Path",
            "Image Modified",
        ]


def infer_student_name_from_path(image_path: str) -> str:
    # Expect: students/<StudentName>/*
    parts = os.path.normpath(image_path).split(os.sep)
    try:
        idx = parts.index("students")
        if idx + 1 < len(parts):
            return parts[idx + 1]
    except ValueError:
        pass
    # Fallback to parent folder name
    if len(parts) >= 2:
        return parts[-2]
    return "Unknown"


def parse_fields_from_text(text: str, image_path: str) -> ParsedFields:
    student_name = infer_student_name_from_path(image_path)

    # Patterns (case-insensitive, flexible separators)
    day_patterns = [
        r"\bday\s*[:#-]?\s*(\d{1,3})\b",
        r"\bD\s*(\d{1,3})\b",
    ]

    accuracy_patterns = [
        r"\baccuracy\s*[:=-]?\s*(\d{1,3}(?:\.\d+)?)\s*%\b",
        r"\bacc\s*[:=-]?\s*(\d{1,3}(?:\.\d+)?)\s*%\b",
    ]

    wpm_patterns = [
        r"\bwords?\s*per\s*minute\s*[:=-]?\s*(\d{1,4})\b",
        r"\bwpm\s*[:=-]?\s*(\d{1,4})\b",
    ]

    course_level_patterns = [
        r"\bcourse\s*completed\s*level\s*[:=-]?\s*([\w./-]{1,32})\b",
        r"\bcourse\s*level\s*[:=-]?\s*([\w./-]{1,32})\b",
    ]

    completed_level_patterns = [
        r"\bcompleted\s*level\s*[:=-]?\s*([\w./-]{1,32})\b",
        r"\blevel\s*completed\s*[:=-]?\s*([\w./-]{1,32})\b",
    ]

    def find_first(patterns: list[str], flags=re.IGNORECASE) -> Optional[str]:
        for pat in patterns:
            m = re.search(pat, text, flags)
            if m:
                return m.group(1)
        return None

    def to_int(val: Optional[str]) -> Optional[int]:
        try:
            return int(val) if val is not None else None
        except ValueError:
            return None

    def to_float(val: Optional[str]) -> Optional[float]:
        try:
            return float(val) if val is not None else None
        except ValueError:
            return None

    day_str = find_first(day_patterns)
    acc_str = find_first(accuracy_patterns)
    wpm_str = find_first(wpm_patterns)
    course_level = find_first(course_level_patterns)
    completed_level = find_first(completed_level_patterns)

    return ParsedFields(
        student_name=student_name,
        day_number=to_int(day_str),
        accuracy_percent=to_float(acc_str),
        words_per_minute=to_int(wpm_str),
        course_completed_level=course_level,
        completed_level=completed_level,
    )

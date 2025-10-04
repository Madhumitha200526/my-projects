import re
from typing import Dict, Optional


_WHITESPACE = re.compile(r"\s+")


def _clean_snippet(text: str, max_len: int = 200) -> str:
    cleaned = _WHITESPACE.sub(" ", text).strip()
    if len(cleaned) > max_len:
        return cleaned[: max_len - 1] + "…"
    return cleaned


def _search_number(patterns, text: str) -> Optional[float]:
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE | re.DOTALL)
        if m:
            num_str = m.group(1)
            try:
                return float(num_str)
            except ValueError:
                # Sometimes numbers like 85% or 120 wpm, remove non-digits and try again
                num_digits = re.sub(r"[^0-9.]+", "", num_str)
                if num_digits:
                    try:
                        return float(num_digits)
                    except ValueError:
                        pass
    return None


def _search_text(patterns, text: str) -> Optional[str]:
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE | re.DOTALL)
        if m:
            value = m.group(1).strip()
            # Normalize common spacing
            value = _WHITESPACE.sub(" ", value)
            return value
    return None


def parse_metrics(ocr_text: str) -> Dict[str, Optional[str]]:
    # Accuracy patterns (captures number optionally followed by %)
    accuracy_patterns = [
        r"\baccuracy\s*[:\-]?\s*(\d{1,3}(?:\.\d+)?)%?\b",
        r"\bacc\.?\s*[:\-]?\s*(\d{1,3}(?:\.\d+)?)%?\b",
    ]

    # WPM patterns
    wpm_patterns = [
        r"\bwords\s*per\s*minute\b[^0-9]{0,10}(\d{1,4})",
        r"\bwpm\b[^0-9]{0,10}(\d{1,4})",
        r"(\d{1,4})\s*\bwpm\b",
    ]

    # Course completed level patterns
    course_level_patterns = [
        r"\bcourse\s*(?:completed\s*)?level\s*[:\-]?\s*([A-Za-z0-9./\- ]{1,20})",
        r"\bcourse\s*level\s*[:\-]?\s*([A-Za-z0-9./\- ]{1,20})",
    ]

    # Completed level patterns
    completed_level_patterns = [
        r"\bcompleted\s*level\s*[:\-]?\s*([A-Za-z0-9./\- ]{1,20})",
        r"\blevel\s*completed\s*[:\-]?\s*([A-Za-z0-9./\- ]{1,20})",
        r"\bcompletion\s*[:\-]?\s*([A-Za-z0-9./\- ]{1,20})",
    ]

    accuracy = _search_number(accuracy_patterns, ocr_text)
    wpm = _search_number(wpm_patterns, ocr_text)
    course_level = _search_text(course_level_patterns, ocr_text)
    completed_level = _search_text(completed_level_patterns, ocr_text)

    result = {
        "accuracy": f"{accuracy:.2f}" if accuracy is not None else None,
        "wpm": f"{int(wpm)}" if wpm is not None else None,
        "course_completed_level": course_level,
        "completed_level": completed_level,
        "ocr_snippet": _clean_snippet(ocr_text),
    }
    return result

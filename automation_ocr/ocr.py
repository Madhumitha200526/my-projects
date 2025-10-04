from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional, Dict, Any

import pytesseract
from PIL import Image


@dataclass
class OcrResult:
    text: str
    snippet: str


def configure_tesseract_from_env() -> None:
    tesseract_cmd = os.getenv("TESSERACT_CMD")
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd


def perform_ocr(image_path: str) -> OcrResult:
    configure_tesseract_from_env()
    image = Image.open(image_path)

    # Try a couple of configurations for better accuracy
    oem_psm_variants = [
        (3, 6),  # Default LSTM, assume a block of text
        (1, 3),  # Legacy + LSTM, fully automatic page segmentation
    ]

    text_candidates = []
    for oem, psm in oem_psm_variants:
        config = f"--oem {oem} --psm {psm}"
        try:
            text = pytesseract.image_to_string(image, config=config)
            if text:
                text_candidates.append(text)
        except Exception:
            continue

    final_text = max(text_candidates, key=len) if text_candidates else ""
    snippet = final_text.strip().splitlines()
    snippet = " ".join(snippet[:3])[:280] if snippet else ""

    return OcrResult(text=final_text, snippet=snippet)

from typing import Optional
from PIL import Image, ImageOps
import pytesseract
from .config import SETTINGS


class OCREngine:
    def __init__(self) -> None:
        # Allow overriding tesseract binary path via env
        pytesseract.pytesseract.tesseract_cmd = SETTINGS.tesseract_cmd

    def extract_text(self, image_path: str) -> Optional[str]:
        try:
            with Image.open(image_path) as img:
                # Basic preprocessing for better OCR
                img = img.convert("RGB")
                grayscale = ImageOps.grayscale(img)
                # Slight contrast enhancement by autocontrast
                enhanced = ImageOps.autocontrast(grayscale)
                text = pytesseract.image_to_string(enhanced)
                if not text:
                    # fallback to original image
                    text = pytesseract.image_to_string(img)
                return text
        except Exception:
            return None

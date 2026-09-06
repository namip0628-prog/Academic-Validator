import os
from pathlib import Path
from typing import Dict, Any
from PIL import Image
import pytesseract

from config import TESSERACT_CMD, find_tesseract_binary


def setup_tesseract():
    """Configures pytesseract with the binary path if resolved."""
    cmd = TESSERACT_CMD or find_tesseract_binary()
    if cmd:
        pytesseract.pytesseract.tesseract_cmd = cmd
    return cmd


def is_ocr_available() -> bool:
    """Checks whether the Tesseract executable is reachable and operational."""
    cmd = setup_tesseract()
    if not cmd:
        return False
    try:
        # Check version to verify executable works
        _ = pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def extract_text(image_path: str | Path) -> Dict[str, Any]:
    """
    Performs Optical Character Recognition (OCR) on an image using Tesseract.

    Args:
        image_path: Path to the image file to read (preferably preprocessed).

    Returns:
        Dictionary containing:
            - "success": bool
            - "text": str (extracted raw text)
            - "char_count": int
            - "word_count": int
            - "confidence": float (average confidence score 0-100)
            - "error": Optional[str]
            - "install_guide": Optional[str]
    """
    image_path = Path(image_path)
    if not image_path.exists():
        return {
            "success": False,
            "text": "",
            "char_count": 0,
            "word_count": 0,
            "confidence": 0.0,
            "error": f"Image file not found at: {image_path}",
            "install_guide": None,
        }

    cmd = setup_tesseract()

    try:
        with Image.open(image_path) as pil_img:
            # Custom Tesseract config:
            # --oem 3: Default OCR Engine Mode (LSTM neural net)
            # --psm 3: Fully automatic page segmentation (suits certificates & marksheets)
            custom_config = r"--oem 3 --psm 3"
            raw_text = pytesseract.image_to_string(pil_img, config=custom_config)

            # Extract word data to compute average OCR confidence
            avg_confidence = 0.0
            try:
                data = pytesseract.image_to_data(
                    pil_img, config=custom_config, output_type=pytesseract.Output.DICT
                )
                confidences = [
                    int(c)
                    for c in data.get("conf", [])
                    if str(c).isdigit() and int(c) >= 0
                ]
                if confidences:
                    avg_confidence = round(sum(confidences) / len(confidences), 1)
            except Exception:
                avg_confidence = 0.0

            clean_text = raw_text.strip()
            words = clean_text.split()

            return {
                "success": True,
                "text": clean_text,
                "char_count": len(clean_text),
                "word_count": len(words),
                "confidence": avg_confidence,
                "error": None,
                "install_guide": None,
            }

    except (pytesseract.TesseractNotFoundError, FileNotFoundError):
        return {
            "success": False,
            "text": "",
            "char_count": 0,
            "word_count": 0,
            "confidence": 0.0,
            "error": "Tesseract OCR binary was not detected on this system.",
            "install_guide": (
                "To enable OCR:\n"
                "1. Windows: Run 'winget install UB-Mannheim.TesseractOCR' in an Administrator terminal, "
                "or download the installer from https://github.com/UB-Mannheim/tesseract/wiki\n"
                "2. Default installation path is 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'.\n"
                "3. Set TESSERACT_CMD in your .env file if installed in a custom directory, then restart the server."
            ),
        }
    except Exception as e:
        return {
            "success": False,
            "text": "",
            "char_count": 0,
            "word_count": 0,
            "confidence": 0.0,
            "error": f"OCR processing failed: {str(e)}",
            "install_guide": None,
        }

import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

# File Upload Configuration
UPLOAD_FOLDER = BASE_DIR / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)

MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "tiff", "bmp"}

SECRET_KEY = os.getenv("SECRET_KEY", "dev-academic-validator-key-2026")


def find_tesseract_binary() -> str | None:
    """
    Attempts to locate the Tesseract executable in the system.
    Returns the valid executable path, or None if not found.
    """
    # 1. Explicit environment variable
    custom_cmd = os.getenv("TESSERACT_CMD")
    if custom_cmd and os.path.exists(custom_cmd):
        return custom_cmd

    # 2. System PATH
    which_path = shutil.which("tesseract")
    if which_path:
        return which_path

    # 3. Standard Windows installation paths
    common_windows_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
    ]
    for path in common_windows_paths:
        if os.path.exists(path):
            return path

    return None


TESSERACT_CMD = find_tesseract_binary()

"""
Academic Document Authenticity Validator - Utilities Package
Contains modular components for:
- Document hashing (SHA-256)
- Image preprocessing (OpenCV)
- OCR extraction (Tesseract / pytesseract)
- Academic entity extraction (Regex & Heuristics)
"""

from .hasher import generate_sha256
from .preprocessor import preprocess_image
from .ocr_engine import extract_text, is_ocr_available
from .extractor import extract_academic_fields
from .blockchain import blockchain_manager, BlockchainManager
from .history import add_audit_entry, get_recent_history, get_record_by_id
from .report_generator import generate_verification_pdf

__all__ = [
    "generate_sha256",
    "preprocess_image",
    "extract_text",
    "is_ocr_available",
    "extract_academic_fields",
    "blockchain_manager",
    "BlockchainManager",
    "add_audit_entry",
    "get_recent_history",
    "get_record_by_id",
    "generate_verification_pdf",
]

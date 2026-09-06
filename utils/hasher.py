import hashlib
from pathlib import Path
from typing import Union, BinaryIO


def generate_sha256(source: Union[str, Path, bytes, BinaryIO], chunk_size: int = 65536) -> str:
    """
    Computes the SHA-256 cryptographic hash of a document.

    The SHA-256 digest acts as a unique digital fingerprint. In academic document
    validation, this ensures document immutability: any modification to marks,
    names, or pixels results in an entirely different hash (Avalanche Effect).
    This hash can subsequently be recorded on a blockchain or tamper-evident ledger.

    Args:
        source: File path (str or Path), raw bytes, or a readable binary file-like object.
        chunk_size: Size of memory chunks in bytes when reading files (default: 64 KB).

    Returns:
        A 64-character hexadecimal SHA-256 digest string.
    """
    hasher = hashlib.sha256()

    if isinstance(source, bytes):
        hasher.update(source)
        return hasher.hexdigest()

    if hasattr(source, "read"):
        # Handle file-like objects (e.g., Flask request.files['document'].stream)
        current_pos = None
        if hasattr(source, "tell") and hasattr(source, "seek"):
            try:
                current_pos = source.tell()
                source.seek(0)
            except Exception:
                current_pos = None

        while True:
            chunk = source.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)

        # Reset stream position if possible so subsequent handlers can read it
        if current_pos is not None:
            source.seek(current_pos)

        return hasher.hexdigest()

    file_path = Path(source)
    if not file_path.is_file():
        raise FileNotFoundError(f"Cannot compute hash: file does not exist at '{file_path}'")

    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)

    return hasher.hexdigest()

import os
from pathlib import Path
from typing import Dict, Any, Tuple
import cv2
import numpy as np


def deskew_image(gray_img: np.ndarray) -> Tuple[np.ndarray, float]:
    """
    Detects and corrects skew in scanned documents using minAreaRect on foreground contours.
    Returns (deskewed_image, angle_in_degrees).
    """
    # Invert image: text becomes white, background black
    thresh = cv2.bitwise_not(gray_img)

    # Find coordinates of all foreground pixels
    coords = np.column_stack(np.where(thresh > 0))
    if len(coords) < 100:
        return gray_img, 0.0

    # minAreaRect computes minimum bounding box around text
    angle = cv2.minAreaRect(coords)[-1]

    # Normalize angle from OpenCV's representation
    if angle < -45:
        angle = -(90 + angle)
    elif angle > 45:
        angle = 90 - angle
    else:
        angle = -angle

    # Only deskew if skew is non-trivial and not inverted (between 0.5 and 45 deg)
    if abs(angle) < 0.5 or abs(angle) > 45:
        return gray_img, 0.0

    (h, w) = gray_img.shape[:2]
    center = (w // 2, h // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    deskewed = cv2.warpAffine(
        gray_img,
        rotation_matrix,
        (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE,
    )
    return deskewed, round(float(angle), 2)


def preprocess_image(image_path: str | Path, output_path: str | Path | None = None) -> Dict[str, Any]:
    """
    Preprocesses an academic document/certificate image using OpenCV to optimize OCR accuracy.

    Pipeline:
    1. Robust file loading (supports paths with spaces and Unicode).
    2. Optional resolution upscaling for low-res scans (ensures minimum height for OCR legibility).
    3. Grayscale conversion.
    4. Gaussian denoising to remove scanner grain, dust, and minor paper artifacts.
    5. Deskewing to horizontally align tilted text lines.
    6. Otsu binarization to produce crisp, high-contrast black-and-white text.
    7. Saves preprocessed output for frontend visualization and downstream OCR.

    Args:
        image_path: Path to the original input image.
        output_path: Optional destination path to write the preprocessed image.

    Returns:
        Dictionary with metadata:
            - "processed_path": str path to saved preprocessed image
            - "original_size": (width, height)
            - "processed_size": (width, height)
            - "skew_angle": float degrees rotated
            - "steps_applied": list of step names
    """
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Input image not found: {image_path}")

    # Read image via numpy buffer to prevent Windows path encoding issues
    with open(image_path, "rb") as f:
        file_bytes = np.frombuffer(f.read(), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError(f"OpenCV could not decode image file at: {image_path}")

    orig_h, orig_w = image.shape[:2]
    steps_applied = ["Loaded Original Image"]

    # Optional scaling: If image is too small (width < 1200), upscale for OCR clarity
    if orig_w < 1200:
        scale_factor = 1200 / float(orig_w)
        image = cv2.resize(image, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
        steps_applied.append(f"Upscaled Resolution (x{scale_factor:.2f})")

    # Step 1: Grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    steps_applied.append("Grayscale Conversion")

    # Step 2: Denoising
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    steps_applied.append("Gaussian Denoising")

    # Step 3: Deskewing
    deskewed, skew_angle = deskew_image(blurred)
    if skew_angle != 0.0:
        steps_applied.append(f"Deskew Alignment ({skew_angle}°)")

    # Step 4: Binarization via Otsu's thresholding
    # Academic documents usually have dark text on light backgrounds
    _, binarized = cv2.threshold(deskewed, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    steps_applied.append("Otsu Binarization (High Contrast)")

    # Determine output path
    if output_path is None:
        output_path = image_path.parent / f"processed_{image_path.name}"
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save output image
    success, encoded_img = cv2.imencode(".png", binarized)
    if success:
        with open(output_path, "wb") as f:
            f.write(encoded_img.tobytes())
    else:
        cv2.imwrite(str(output_path), binarized)

    proc_h, proc_w = binarized.shape[:2]

    return {
        "processed_path": str(output_path),
        "original_size": (orig_w, orig_h),
        "processed_size": (proc_w, proc_h),
        "skew_angle": skew_angle,
        "steps_applied": steps_applied,
    }

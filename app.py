import os
import uuid
from pathlib import Path
from flask import Flask, request, jsonify, render_template, send_from_directory, send_file
from werkzeug.utils import secure_filename
import cv2

import config
from utils.hasher import generate_sha256
from utils.preprocessor import preprocess_image
from utils.ocr_engine import extract_text, is_ocr_available, setup_tesseract
from utils.extractor import extract_academic_fields
from utils.blockchain import blockchain_manager
from utils.history import add_audit_entry, get_recent_history, get_record_by_id
from utils.report_generator import generate_verification_pdf

app = Flask(__name__)
app.config["SECRET_KEY"] = config.SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH
app.config["UPLOAD_FOLDER"] = config.UPLOAD_FOLDER


def is_allowed_file(filename: str) -> bool:
    """Checks if file extension is allowed."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in config.ALLOWED_EXTENSIONS
    )


@app.route("/")
def index():
    """Renders the unified Academic Document Authenticity Validator dashboard."""
    ocr_ready = is_ocr_available()
    bc_status = blockchain_manager.get_status()
    return render_template("index.html", ocr_ready=ocr_ready, blockchain=bc_status)


@app.route("/api/system-status", methods=["GET"])
def system_status():
    """Returns backend health, OpenCV version, OCR engine readiness, and blockchain network status."""
    tesseract_path = setup_tesseract()
    ocr_ready = is_ocr_available()
    bc_status = blockchain_manager.get_status()

    return jsonify({
        "status": "online",
        "ocr_available": ocr_ready,
        "tesseract_path": tesseract_path or "Not Detected",
        "opencv_version": cv2.__version__,
        "max_upload_mb": config.MAX_CONTENT_LENGTH // (1024 * 1024),
        "allowed_extensions": list(config.ALLOWED_EXTENSIONS),
        "blockchain": bc_status,
    })


@app.route("/api/blockchain-status", methods=["GET"])
def get_blockchain_status():
    """Returns real-time Ethereum node and smart contract status."""
    return jsonify(blockchain_manager.get_status())


@app.route("/api/validate", methods=["POST"])
def validate_document():
    """
    Step 1: Document OCR Extraction & Fingerprint generation.
    Used by institutions to preview extracted fields before blockchain anchoring.
    """
    if "document" not in request.files:
        return jsonify({"success": False, "error": "No document file provided in request."}), 400

    file = request.files["document"]
    if not file or file.filename == "":
        return jsonify({"success": False, "error": "No selected file."}), 400

    if not is_allowed_file(file.filename):
        allowed = ", ".join(sorted(config.ALLOWED_EXTENSIONS))
        return jsonify({
            "success": False,
            "error": f"Unsupported file type. Please upload one of: {allowed}",
        }), 400

    original_filename = secure_filename(file.filename) or "academic_document.png"
    unique_id = uuid.uuid4().hex[:10]
    saved_filename = f"{unique_id}_{original_filename}"
    original_save_path = config.UPLOAD_FOLDER / saved_filename

    try:
        file.save(str(original_save_path))

        # 1. Cryptographic SHA-256 Hashing
        sha256_hash = generate_sha256(original_save_path)

        # 2. OpenCV Image Preprocessing
        processed_filename = f"proc_{unique_id}_{original_filename}"
        processed_save_path = config.UPLOAD_FOLDER / processed_filename

        preprocess_meta = preprocess_image(
            image_path=original_save_path,
            output_path=processed_save_path,
        )

        # 3. OCR Text Extraction
        ocr_result = extract_text(processed_save_path)

        # 4. Academic Field Parsing
        extracted_data = extract_academic_fields(ocr_result["text"])

        # Check if hash is already on blockchain
        on_chain_check = blockchain_manager.verify_document(sha256_hash)

        return jsonify({
            "success": True,
            "filename": original_filename,
            "sha256_hash": sha256_hash,
            "original_image_url": f"/uploads/{saved_filename}",
            "processed_image_url": f"/uploads/{processed_filename}",
            "preprocessing": {
                "steps_applied": preprocess_meta["steps_applied"],
                "skew_angle": preprocess_meta["skew_angle"],
                "original_dimensions": f"{preprocess_meta['original_size'][0]}x{preprocess_meta['original_size'][1]} px",
                "processed_dimensions": f"{preprocess_meta['processed_size'][0]}x{preprocess_meta['processed_size'][1]} px",
            },
            "ocr": {
                "success": ocr_result["success"],
                "raw_text": ocr_result["text"],
                "char_count": ocr_result["char_count"],
                "word_count": ocr_result["word_count"],
                "confidence": ocr_result["confidence"],
                "error": ocr_result["error"],
                "install_guide": ocr_result["install_guide"],
            },
            "academic_data": extracted_data,
            "already_on_chain": on_chain_check["is_authentic"],
            "on_chain_record": on_chain_check if on_chain_check["is_authentic"] else None,
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Server error processing document: {str(e)}",
        }), 500


@app.route("/api/validate-sample", methods=["POST"])
def validate_sample():
    """Triggers the OCR & hashing pipeline on the built-in sample certificate."""
    sample_file = Path(__file__).resolve().parent / "samples" / "sample_degree_certificate.png"
    if not sample_file.exists():
        from samples.generate_sample import generate_sample_certificate
        generate_sample_certificate(sample_file)

    original_filename = "sample_degree_certificate.png"
    unique_id = uuid.uuid4().hex[:10]
    saved_filename = f"{unique_id}_{original_filename}"
    original_save_path = config.UPLOAD_FOLDER / saved_filename

    with open(sample_file, "rb") as src, open(original_save_path, "wb") as dst:
        dst.write(src.read())

    sha256_hash = generate_sha256(original_save_path)
    processed_filename = f"proc_{unique_id}_{original_filename}"
    processed_save_path = config.UPLOAD_FOLDER / processed_filename

    preprocess_meta = preprocess_image(
        image_path=original_save_path,
        output_path=processed_save_path,
    )

    ocr_result = extract_text(processed_save_path)
    extracted_data = extract_academic_fields(ocr_result["text"])
    on_chain_check = blockchain_manager.verify_document(sha256_hash)

    return jsonify({
        "success": True,
        "filename": "sample_degree_certificate.png",
        "sha256_hash": sha256_hash,
        "original_image_url": f"/uploads/{saved_filename}",
        "processed_image_url": f"/uploads/{processed_filename}",
        "preprocessing": {
            "steps_applied": preprocess_meta["steps_applied"],
            "skew_angle": preprocess_meta["skew_angle"],
            "original_dimensions": f"{preprocess_meta['original_size'][0]}x{preprocess_meta['original_size'][1]} px",
            "processed_dimensions": f"{preprocess_meta['processed_size'][0]}x{preprocess_meta['processed_size'][1]} px",
        },
        "ocr": {
            "success": ocr_result["success"],
            "raw_text": ocr_result["text"],
            "char_count": ocr_result["char_count"],
            "word_count": ocr_result["word_count"],
            "confidence": ocr_result["confidence"],
            "error": ocr_result["error"],
            "install_guide": ocr_result["install_guide"],
        },
        "academic_data": extracted_data,
        "already_on_chain": on_chain_check["is_authentic"],
        "on_chain_record": on_chain_check if on_chain_check["is_authentic"] else None,
    })


@app.route("/api/register", methods=["POST"])
def register_on_blockchain():
    """
    Anchors document SHA-256 hash and metadata onto the blockchain smart contract.
    CRITICAL: The document itself is NOT uploaded to the blockchain.
    """
    data = request.get_json() or {}

    document_hash = data.get("document_hash")
    if not document_hash or len(document_hash.replace("0x", "")) != 64:
        return jsonify({"success": False, "error": "A valid 64-character SHA-256 hash is required."}), 400

    student_name = data.get("student_name", "Aarav Sharma")
    student_id = data.get("student_id", "1NT20CS045")
    institution = data.get("institution", "National Institute of Technology")
    course = data.get("course", "Bachelor of Technology in Computer Science")
    marks = data.get("marks", "CGPA: 8.85 / 10.0")
    document_name = data.get("document_name", "academic_credential.png")

    result = blockchain_manager.register_document(
        document_hash_hex=document_hash,
        student_name=student_name,
        student_id=student_id,
        institution=institution,
        course=course,
        marks=marks,
    )

    if not result.get("success"):
        return jsonify(result), 400

    # Record in persistent audit history
    record_id = add_audit_entry(
        event_type="REGISTRATION",
        document_name=document_name,
        document_hash=document_hash,
        student_name=student_name,
        student_id=student_id,
        institution=institution,
        course=course,
        marks=marks,
        verdict="REGISTERED",
        tx_hash=result.get("transaction_hash"),
        block_number=result.get("block_number"),
    )
    result["record_id"] = record_id

    return jsonify(result)


@app.route("/api/verify", methods=["POST"])
def verify_document_authenticity():
    """
    Phase 3: Public Authenticity Verification.
    1. Receives uploaded academic document.
    2. Calculates SHA-256 cryptographic hash.
    3. Queries smart contract on blockchain.
    4. Returns verification verdict:
       ✓ AUTHENTIC: hash matches on-chain record
       ✗ INVALID_OR_MODIFIED: no match found on ledger
    """
    if "document" not in request.files:
        return jsonify({"success": False, "error": "No document provided for verification."}), 400

    file = request.files["document"]
    if not file or file.filename == "":
        return jsonify({"success": False, "error": "No selected file."}), 400

    original_filename = secure_filename(file.filename) or "verify_doc.png"
    unique_id = uuid.uuid4().hex[:10]
    saved_filename = f"verify_{unique_id}_{original_filename}"
    save_path = config.UPLOAD_FOLDER / saved_filename

    try:
        file.save(str(save_path))

        # 1. Generate SHA-256 fingerprint
        document_hash = generate_sha256(save_path)

        # 2. Query Blockchain
        verification_result = blockchain_manager.verify_document(document_hash)

        # 3. Add to persistent audit history
        verdict = "AUTHENTIC" if verification_result["is_authentic"] else "INVALID_OR_MODIFIED"
        record_id = add_audit_entry(
            event_type="VERIFICATION",
            document_name=original_filename,
            document_hash=document_hash,
            student_name=verification_result.get("student_name"),
            student_id=verification_result.get("student_id"),
            institution=verification_result.get("institution"),
            course=verification_result.get("course"),
            marks=verification_result.get("marks"),
            verdict=verdict,
            tx_hash=verification_result.get("transaction_hash"),
            block_number=verification_result.get("block_number"),
        )

        verification_result["record_id"] = record_id
        verification_result["filename"] = original_filename
        verification_result["preview_url"] = f"/uploads/{saved_filename}"

        return jsonify({
            "success": True,
            "verification": verification_result,
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Verification failed: {str(e)}",
        }), 500


@app.route("/api/verify-sample", methods=["POST"])
def verify_sample():
    """Verifies the built-in sample certificate against the blockchain."""
    sample_file = Path(__file__).resolve().parent / "samples" / "sample_degree_certificate.png"
    if not sample_file.exists():
        from samples.generate_sample import generate_sample_certificate
        generate_sample_certificate(sample_file)

    document_hash = generate_sha256(sample_file)
    verification_result = blockchain_manager.verify_document(document_hash)

    verdict = "AUTHENTIC" if verification_result["is_authentic"] else "INVALID_OR_MODIFIED"
    record_id = add_audit_entry(
        event_type="VERIFICATION",
        document_name="sample_degree_certificate.png",
        document_hash=document_hash,
        student_name=verification_result.get("student_name"),
        student_id=verification_result.get("student_id"),
        institution=verification_result.get("institution"),
        course=verification_result.get("course"),
        marks=verification_result.get("marks"),
        verdict=verdict,
        tx_hash=verification_result.get("transaction_hash"),
        block_number=verification_result.get("block_number"),
    )

    verification_result["record_id"] = record_id
    verification_result["filename"] = "sample_degree_certificate.png"
    verification_result["preview_url"] = "/api/sample-certificate"

    return jsonify({
        "success": True,
        "verification": verification_result,
    })


@app.route("/api/history", methods=["GET"])
def get_history():
    """Returns recent registration and verification audit history."""
    records = get_recent_history(limit=25)
    return jsonify({
        "success": True,
        "count": len(records),
        "history": records,
    })


@app.route("/api/download-report/<int:record_id>", methods=["GET"])
def download_verification_report(record_id: int):
    """Generates and downloads a formal PDF Authenticity Verification Report."""
    record = get_record_by_id(record_id)
    if not record:
        return jsonify({"success": False, "error": f"Record #{record_id} not found"}), 404

    pdf_buffer = generate_verification_pdf(record)
    download_name = f"authenticity_report_{record_id}_{record['document_hash'][:8]}.pdf"

    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=download_name,
    )


@app.route("/uploads/<path:filename>")
def serve_upload(filename: str):
    """Serves uploaded and preprocessed images to the browser."""
    return send_from_directory(config.UPLOAD_FOLDER, filename)


@app.route("/api/sample-certificate")
def get_sample_certificate():
    """Serves the sample academic certificate."""
    sample_dir = Path(__file__).resolve().parent / "samples"
    return send_from_directory(sample_dir, "sample_degree_certificate.png")


if __name__ == "__main__":
    print("=================================================================")
    print(" Academic Document Authenticity Validator Server")
    print(" Architecture: OCR + SHA-256 Cryptography + Ethereum Blockchain")
    print(f" Upload directory: {config.UPLOAD_FOLDER}")
    print(f" Tesseract OCR Status: {'CONNECTED' if is_ocr_available() else 'NOT FOUND'}")
    print(f" Blockchain Node: {blockchain_manager.get_status()['mode']}")
    print(" Starting on http://127.0.0.1:5000 ...")
    print("=================================================================")
    app.run(host="127.0.0.1", port=5000, debug=True)

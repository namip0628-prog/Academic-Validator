import io
from pathlib import Path
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable


def generate_verification_pdf(record_data: Dict[str, Any]) -> io.BytesIO:
    """
    Generates a formal, printable PDF Academic Credential Authenticity Certificate.

    Args:
        record_data: Dictionary with verification details, metadata, and transaction hash.

    Returns:
        BytesIO stream containing the generated PDF document.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CertTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a"),
        alignment=1,  # Center
    )

    subtitle_style = ParagraphStyle(
        "CertSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569"),
        alignment=1,
    )

    verdict_style = ParagraphStyle(
        "VerdictBanner",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#065f46"),
        alignment=1,
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        textColor=colors.HexColor("#334155"),
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        textColor=colors.HexColor("#0f172a"),
    )

    mono_style = ParagraphStyle(
        "MonoCell",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8,
        textColor=colors.HexColor("#1e293b"),
    )

    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#64748b"),
        alignment=1,
    )

    story = []

    # Title & Header
    story.append(Paragraph("ACADEMIC CREDENTIAL AUTHENTICITY REPORT", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Cryptographic Fingerprint & Blockchain Audit Trail", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1e3a8a"), spaceAfter=15))

    # Verification Verdict Banner
    is_authentic = record_data.get("verdict", "").upper() in ["AUTHENTIC", "REGISTERED"]
    verdict_text = "✓ VERIFIED AUTHENTIC — IMMUTABLE BLOCKCHAIN RECORD" if is_authentic else "✗ INVALID OR TAMPERED CREDENTIAL"
    verdict_color = colors.HexColor("#d1fae5") if is_authentic else colors.HexColor("#fee2e2")
    verdict_border = colors.HexColor("#059669") if is_authentic else colors.HexColor("#dc2626")
    verdict_text_color = colors.HexColor("#065f46") if is_authentic else colors.HexColor("#991b1b")

    verdict_para = Paragraph(f"<font color='{verdict_text_color.hexval()}'><b>{verdict_text}</b></font>", verdict_style)
    verdict_table = Table([[verdict_para]], colWidths=[530])
    verdict_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), verdict_color),
        ("BOX", (0, 0), (-1, -1), 1.5, verdict_border),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    story.append(verdict_table)
    story.append(Spacer(1, 15))

    # Section 1: Cryptographic Fingerprint
    story.append(Paragraph("<b>1. Cryptographic Document Fingerprint</b>", styles["Heading3"]))
    story.append(Spacer(1, 6))

    hash_data = [
        [Paragraph("Document Name", table_header_style), Paragraph(record_data.get("document_name", "-"), table_cell_style)],
        [Paragraph("SHA-256 Hash", table_header_style), Paragraph(record_data.get("document_hash", "-"), mono_style)],
        [Paragraph("Audit Timestamp", table_header_style), Paragraph(record_data.get("formatted_date", "-"), table_cell_style)],
    ]
    t1 = Table(hash_data, colWidths=[150, 380])
    t1.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t1)
    story.append(Spacer(1, 15))

    # Section 2: Blockchain Smart Contract Proof
    story.append(Paragraph("<b>2. Blockchain Ledger Anchor Details</b>", styles["Heading3"]))
    story.append(Spacer(1, 6))

    tx_hash = record_data.get("tx_hash", "-")
    block_num = str(record_data.get("block_number", "-"))

    chain_data = [
        [Paragraph("Blockchain Network", table_header_style), Paragraph("Ethereum / Hardhat EVM (Localnet)", table_cell_style)],
        [Paragraph("Smart Contract", table_header_style), Paragraph("AcademicValidator.sol", table_cell_style)],
        [Paragraph("Transaction Hash", table_header_style), Paragraph(tx_hash, mono_style)],
        [Paragraph("Block Number", table_header_style), Paragraph(block_num, table_cell_style)],
        [Paragraph("On-Chain Timestamp", table_header_style), Paragraph(record_data.get("formatted_date", "-"), table_cell_style)],
    ]
    t2 = Table(chain_data, colWidths=[150, 380])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t2)
    story.append(Spacer(1, 15))

    # Section 3: Verified Academic Metadata
    story.append(Paragraph("<b>3. Verified Academic Credential Metadata</b>", styles["Heading3"]))
    story.append(Spacer(1, 6))

    meta_data = [
        [Paragraph("Student Name", table_header_style), Paragraph(record_data.get("student_name", "-"), table_cell_style)],
        [Paragraph("Student ID / USN", table_header_style), Paragraph(record_data.get("student_id", "-"), table_cell_style)],
        [Paragraph("Issuing Institution", table_header_style), Paragraph(record_data.get("institution", "-"), table_cell_style)],
        [Paragraph("Course / Degree", table_header_style), Paragraph(record_data.get("course", "-"), table_cell_style)],
        [Paragraph("Grade / Marks / CGPA", table_header_style), Paragraph(record_data.get("marks", "-"), table_cell_style)],
    ]
    t3 = Table(meta_data, colWidths=[150, 380])
    t3.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t3)
    story.append(Spacer(1, 20))

    # Disclaimer
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#94a3b8"), spaceAfter=10))
    disclaimer_text = (
        "CONFIDENTIALITY & INTEGRITY NOTICE: This verification report was generated through direct cryptographic "
        "inspection against the decentralized smart contract ledger. In compliance with student data privacy laws, "
        "the raw academic document file is never stored on the public blockchain; only the 256-bit hash fingerprint "
        "and verifiable metadata are anchored. Any tampering with marks, names, or individual pixels produces a "
        "non-matching hash, rendering the document instantly invalid."
    )
    story.append(Paragraph(disclaimer_text, disclaimer_style))

    doc.build(story)
    buffer.seek(0)
    return buffer

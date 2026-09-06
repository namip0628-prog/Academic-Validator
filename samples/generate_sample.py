from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def generate_sample_certificate(output_path: Path):
    """
    Generates a clean synthetic academic grade card / certificate
    with known academic fields for testing and demonstration.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    width = 1200
    height = 850
    background_color = (252, 252, 250)
    primary_color = (18, 30, 49)
    accent_color = (20, 75, 140)
    gold_color = (160, 120, 40)
    border_color = (180, 190, 205)

    img = Image.new("RGB", (width, height), color=background_color)
    draw = ImageDraw.Draw(img)

    # Outer and inner ornamental borders
    draw.rectangle([(25, 25), (width - 25, height - 25)], outline=gold_color, width=3)
    draw.rectangle([(35, 35), (width - 35, height - 35)], outline=border_color, width=1)

    # Use default font or simple bitmap font
    font = ImageFont.load_default()

    # Draw header banner
    draw.text((width // 2, 80), "NATIONAL INSTITUTE OF TECHNOLOGY & ADVANCED STUDIES", fill=primary_color, font=font, anchor="mm")
    draw.text((width // 2, 110), "Accredited Grade 'A++' | Autonomous University", fill=accent_color, font=font, anchor="mm")
    draw.text((width // 2, 150), "OFFICIAL STATEMENT OF MARKS & DEGREE CONFERMENT", fill=gold_color, font=font, anchor="mm")

    # Divider line
    draw.line([(80, 180), (width - 80, 180)], fill=border_color, width=2)

    # Certificate body text
    body_y = 230
    line_gap = 40

    records = [
        ("Candidate's Name:", "Aarav Sharma"),
        ("University Seat Number (USN):", "1NT20CS045"),
        ("Institution / College:", "Department of Computer Science & Engineering"),
        ("Degree & Programme:", "Bachelor of Technology in Computer Science"),
        ("Cumulative Grade Point Average (CGPA):", "CGPA: 8.85 / 10.0"),
        ("Division / Classification:", "First Class with Distinction"),
        ("Date of Issue:", "24/07/2024"),
    ]

    for label, val in records:
        draw.text((120, body_y), label, fill=(80, 90, 105), font=font)
        draw.text((450, body_y), val, fill=primary_color, font=font)
        body_y += line_gap

    # Detailed Semester Grade Table
    table_y = body_y + 30
    draw.line([(80, table_y), (width - 80, table_y)], fill=border_color, width=1)
    draw.text((100, table_y + 15), "Subject Code", fill=accent_color, font=font)
    draw.text((260, table_y + 15), "Subject Description", fill=accent_color, font=font)
    draw.text((700, table_y + 15), "Credits", fill=accent_color, font=font)
    draw.text((850, table_y + 15), "Grade", fill=accent_color, font=font)
    draw.text((980, table_y + 15), "Status", fill=accent_color, font=font)
    draw.line([(80, table_y + 35), (width - 80, table_y + 35)], fill=border_color, width=1)

    subjects = [
        ("CS801", "Cryptography and Network Security", "4.0", "O (Outstanding)", "PASS"),
        ("CS802", "Blockchain Technologies & Ledgers", "4.0", "A+ (Excellent)", "PASS"),
        ("CS803", "Machine Learning & Image Processing", "4.0", "O (Outstanding)", "PASS"),
        ("CS804", "Major Project Dissertation & Defense", "6.0", "O (Outstanding)", "PASS"),
    ]

    row_y = table_y + 50
    for code, title, cred, grd, stat in subjects:
        draw.text((100, row_y), code, fill=primary_color, font=font)
        draw.text((260, row_y), title, fill=primary_color, font=font)
        draw.text((720, row_y), cred, fill=primary_color, font=font)
        draw.text((850, row_y), grd, fill=primary_color, font=font)
        draw.text((980, row_y), stat, fill=(20, 130, 60), font=font)
        row_y += 30

    # Verification footer
    draw.line([(80, height - 120), (width - 80, height - 120)], fill=border_color, width=1)
    draw.text((120, height - 80), "Dean of Academic Affairs", fill=(100, 110, 120), font=font)
    draw.text((width // 2, height - 80), "[ Digital Seal of Authenticity ]", fill=accent_color, font=font, anchor="mm")
    draw.text((width - 250, height - 80), "Controller of Examinations", fill=(100, 110, 120), font=font)

    img.save(str(output_path), quality=95)
    print(f"Generated sample academic certificate at: {output_path}")


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "sample_degree_certificate.png"
    generate_sample_certificate(out)

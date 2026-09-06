import re
from typing import Dict, Any, Optional


def clean_field_value(val: Optional[str]) -> Optional[str]:
    """Sanitizes extracted field strings."""
    if not val:
        return None
    val = val.strip()
    # Strip common trailing separators
    val = re.sub(r"^[ :\-\|\.\,]+|[ :\-\|\.\,]+$", "", val)
    # Collapse multiple whitespaces
    val = re.sub(r"\s+", " ", val)
    return val if len(val) >= 2 else None


def extract_student_name(text: str, lines: list[str]) -> tuple[Optional[str], str]:
    """
    Extracts student name using explicit labels and certification phrasing.
    Returns (extracted_name, confidence).
    """
    blacklist = ["university", "college", "institute", "technology", "marks", "grade", "examination", "roll no", "usn"]

    for line in lines:
        line_clean = line.strip()

        # 1. High-confidence explicit label on single line
        explicit_match = re.search(
            r"(?:Candidate(?:'s)?\s*Name|Student\s*Name|Name\s*of\s*(?:the\s*)?(?:Candidate|Student)|Name)\s*[:\-]\s*([A-Za-z\s\.\']{3,40})",
            line_clean,
            re.IGNORECASE,
        )
        if explicit_match:
            candidate = clean_field_value(explicit_match.group(1))
            if candidate and not any(b in candidate.lower() for b in blacklist):
                return candidate, "high"

        # 2. Certification phrasing: "This is to certify that [Mr./Ms.] [Name] has..."
        cert_match = re.search(
            r"(?:certify\s+that|certifies\s+that)\s+(?:(?:Mr\.|Ms\.|Mrs\.|Shri)\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b",
            line_clean,
            re.IGNORECASE,
        )
        if cert_match:
            candidate = clean_field_value(cert_match.group(1))
            if candidate and not any(b in candidate.lower() for b in blacklist):
                return candidate, "high"

        # 3. Honorific prefix on line
        honorific_match = re.search(
            r"\b(?:Mr\.|Ms\.|Mrs\.|Kumari|Shri)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b",
            line_clean,
        )
        if honorific_match:
            candidate = clean_field_value(honorific_match.group(1))
            if candidate and not any(b in candidate.lower() for b in blacklist):
                return candidate, "medium"

    return None, "none"


def extract_student_id(text: str) -> tuple[Optional[str], str]:
    """
    Extracts Student ID, USN, Roll Number, or Registration Number.
    Returns (extracted_id, confidence).
    """
    # 1. Explicit labeled matching (line-aware)
    labeled_patterns = [
        r"(?:USN|University\s*Seat\s*Number)\s*[:\-]?\s*([0-9A-Z]{9,12})\b",
        r"(?:Roll\s*(?:No|Number)|Registration\s*(?:No|Number)|Reg(?:\.|\s*)?No|Enrollment\s*(?:No|Number)|Student\s*ID)\s*[:\-]?\s*([A-Za-z0-9\-\/]{4,20})\b",
    ]
    for pat in labeled_patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            candidate = clean_field_value(match.group(1))
            if candidate:
                return candidate.upper(), "high"

    # 2. Heuristic: Standard VTU/University USN pattern (e.g. 1NT20CS045, 1BM20CS045, 1RV19EC012)
    usn_pattern = r"\b([1-4][A-Z]{2}\d{2}[A-Z]{2}\d{3})\b"
    usn_match = re.search(usn_pattern, text)
    if usn_match:
        return usn_match.group(1).upper(), "high"

    # 3. Generic ID pattern (e.g. ID: CS-2024-089)
    generic_id = re.search(r"\b(?:ID|REG)[-:\s]+([A-Z0-9\-_]{6,15})\b", text, re.IGNORECASE)
    if generic_id:
        return generic_id.group(1).upper(), "medium"

    return None, "none"


def extract_institution(text: str, lines: list[str]) -> tuple[Optional[str], str]:
    """
    Extracts College, University, or Awarding Board name.
    Returns (extracted_institution, confidence).
    """
    # 1. Header scan: Look in the first 8 lines for University/Institute keywords
    institution_keywords = [
        "university",
        "institute of technology",
        "college of engineering",
        "polytechnic",
        "academy of higher education",
        "board of secondary education",
        "national institute",
    ]
    for line in lines[:8]:
        line_clean = line.strip()
        lower_line = line_clean.lower()
        if any(keyword in lower_line for keyword in institution_keywords):
            if 6 <= len(line_clean) <= 85:
                return line_clean, "high"

    # 2. Labeled pattern
    label_match = re.search(
        r"(?:University|Institution|College|Academy|Institute)\s*[:\-]\s*([^\n\r]{5,60})",
        text,
        re.IGNORECASE,
    )
    if label_match:
        candidate = clean_field_value(label_match.group(1))
        if candidate:
            return candidate, "high"

    # 3. Regex match anywhere for full name pattern
    broad_match = re.search(
        r"([A-Z][A-Za-z\s&,\.]{4,40}(?:University|Institute of Technology|College of Engineering|Polytechnic Institute|Institute))",
        text,
    )
    if broad_match:
        candidate = clean_field_value(broad_match.group(1))
        if candidate and len(candidate) > 5:
            return candidate, "medium"

    return None, "none"


def extract_course_or_degree(text: str) -> tuple[Optional[str], str]:
    """
    Extracts Degree, Course, or Specialization.
    Returns (extracted_course, confidence).
    """
    # 1. Labeled pattern
    labeled_match = re.search(
        r"(?:Degree\s*(?:&|and)?\s*Programme|Degree|Programme|Program|Course|Branch|Discipline)\s*[:\-]\s*([A-Za-z\s&\.\(\)]{4,60})",
        text,
        re.IGNORECASE,
    )
    if labeled_match:
        candidate = clean_field_value(labeled_match.group(1))
        if candidate:
            return candidate, "high"

    # 2. Known Degree designations
    degree_patterns = [
        r"\b(Bachelor\s+of\s+[A-Za-z\s&]+(?:\([A-Za-z\s&]+\))?)",
        r"\b(Master\s+of\s+[A-Za-z\s&]+(?:\([A-Za-z\s&]+\))?)",
        r"\b(Doctor\s+of\s+[A-Za-z\s&]+)",
        r"\b(Diploma\s+in\s+[A-Za-z\s&]+)",
        r"\b(B\.?Tech(?:\.?|\s+in|\s*-\s*)(?:[A-Za-z\s&]{3,40}))",
        r"\b(B\.?E\.?(?:\.?|\s+in|\s*-\s*)(?:[A-Za-z\s&]{3,40}))",
        r"\b(M\.?Tech(?:\.?|\s+in|\s*-\s*)(?:[A-Za-z\s&]{3,40}))",
        r"\b(B\.?Sc(?:\.?|\s+in|\s*-\s*)(?:[A-Za-z\s&]{3,40}))",
        r"\b(M\.?Sc(?:\.?|\s+in|\s*-\s*)(?:[A-Za-z\s&]{3,40}))",
        r"\b(B\.?C\.?A|M\.?C\.?A|B\.?B\.?A|M\.?B\.?A|B\.?Com)\b",
    ]
    for pat in degree_patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            candidate = clean_field_value(match.group(1))
            if candidate and len(candidate) >= 3:
                return candidate, "high"

    return None, "none"


def extract_marks_or_grade(text: str) -> tuple[Optional[str], str]:
    """
    Extracts CGPA, GPA, Percentage, Total Marks, or Grade.
    Returns (extracted_marks, confidence).
    """
    # 1. CGPA / GPA
    cgpa_match = re.search(
        r"(?:Cumulative\s*Grade\s*Point\s*Average\s*\(CGPA\)|CGPA|GPA|OGPA|SGPA)\s*[:\-\=]?\s*([0-9]\.[0-9]{1,3}(?:\s*\/\s*10(?:\.0)?)?|\b10\.0\b)",
        text,
        re.IGNORECASE,
    )
    if cgpa_match:
        val = cgpa_match.group(1).strip()
        prefix = "CGPA: " if "cgpa" in cgpa_match.group(0).lower() else "GPA: "
        return f"{prefix}{val}", "high"

    # 2. Percentage
    pct_match = re.search(
        r"\b(?:Percentage|Aggregate|Total\s*%)\s*[:\-\=]?\s*([0-9]{2}(?:\.[0-9]{1,2})?)\s*%",
        text,
        re.IGNORECASE,
    )
    if pct_match:
        return f"{pct_match.group(1)}%", "high"

    # 3. Fraction Marks: e.g. 845 / 1000
    marks_match = re.search(
        r"(?:Marks\s*Obtained|Total\s*Marks|Grand\s*Total)\s*[:\-\=]?\s*([0-9]{2,4}\s*\/\s*[0-9]{2,4})",
        text,
        re.IGNORECASE,
    )
    if marks_match:
        return f"Marks: {marks_match.group(1)}", "high"

    # 4. Class / Division / Grade
    class_match = re.search(
        r"\b(First\s+Class\s+with\s+Distinction|First\s+Class|Second\s+Class|Distinction)\b",
        text,
        re.IGNORECASE,
    )
    if class_match:
        return f"Grade: {class_match.group(1).title()}", "medium"

    return None, "none"


def extract_date_or_year(text: str) -> tuple[Optional[str], str]:
    """
    Extracts Issue Date, Passing Date, or Academic Year.
    Returns (extracted_date, confidence).
    """
    # 1. Labeled Date
    labeled_date = re.search(
        r"(?:Date\s*of\s*Issue|Date|Dated|Issue\s*Date|Issued\s*On)\s*[:\-]\s*([0-9]{1,2}[\/\-\.][0-9]{1,2}[\/\-\.][0-9]{2,4}|[A-Za-z]+\s+[0-9]{1,2},?\s+[0-9]{4}|[0-9]{1,2}\s+[A-Za-z]+,?\s+[0-9]{4})",
        text,
        re.IGNORECASE,
    )
    if labeled_date:
        candidate = clean_field_value(labeled_date.group(1))
        if candidate:
            return candidate, "high"

    # 2. Year of Passing: e.g. "Year of Passing: 2024" or "Month & Year: June 2024"
    passing_match = re.search(
        r"(?:Year\s*of\s*Passing|Passing\s*Year|Month\s*(?:&|and)\s*Year)\s*[:\-]?\s*([A-Za-z]*\s*[0-9]{4})",
        text,
        re.IGNORECASE,
    )
    if passing_match:
        candidate = clean_field_value(passing_match.group(1))
        if candidate:
            return candidate, "high"

    # 3. Formatted calendar date match (DD/MM/YYYY or YYYY-MM-DD)
    date_match = re.search(r"\b([0-3]?[0-9][\/\-\.][0-1]?[0-9][\/\-\.](?:20|19)[0-9]{2})\b", text)
    if date_match:
        return date_match.group(1), "medium"

    # 4. Month YYYY (e.g., July 2024, May 2023)
    month_year = re.search(
        r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(20[1-3][0-9])\b",
        text,
        re.IGNORECASE,
    )
    if month_year:
        return f"{month_year.group(1).capitalize()} {month_year.group(2)}", "medium"

    return None, "none"


def extract_academic_fields(raw_text: str) -> Dict[str, Any]:
    """
    Parses raw OCR text and extracts standardized academic fields.

    Fields extracted:
    - student_name: Student / Candidate Name
    - student_id: USN / Roll No / Registration Number
    - institution: University, College, or Awarding Body
    - course: Degree, Programme, or Branch
    - marks: CGPA, GPA, Percentage, or Division
    - date: Date of Issue or Passing Year

    Returns a structured dictionary with field values, display labels, and confidence levels.
    """
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

    name_val, name_conf = extract_student_name(raw_text, lines)
    id_val, id_conf = extract_student_id(raw_text)
    inst_val, inst_conf = extract_institution(raw_text, lines)
    course_val, course_conf = extract_course_or_degree(raw_text)
    marks_val, marks_conf = extract_marks_or_grade(raw_text)
    date_val, date_conf = extract_date_or_year(raw_text)

    fields = {
        "student_name": {
            "label": "Student Name",
            "value": name_val,
            "confidence": name_conf,
            "icon": "user",
        },
        "student_id": {
            "label": "Student ID / USN",
            "value": id_val,
            "confidence": id_conf,
            "icon": "id-card",
        },
        "institution": {
            "label": "Institution / University",
            "value": inst_val,
            "confidence": inst_conf,
            "icon": "building-columns",
        },
        "course": {
            "label": "Course / Degree",
            "value": course_val,
            "confidence": course_conf,
            "icon": "graduation-cap",
        },
        "marks": {
            "label": "Marks / CGPA / Grade",
            "value": marks_val,
            "confidence": marks_conf,
            "icon": "award",
        },
        "date": {
            "label": "Date of Issue / Passing",
            "value": date_val,
            "confidence": date_conf,
            "icon": "calendar-days",
        },
    }

    # Calculate overall extraction completeness
    detected_count = sum(1 for f in fields.values() if f["value"] is not None)
    total_fields = len(fields)

    return {
        "fields": fields,
        "summary": {
            "detected_fields": detected_count,
            "total_fields": total_fields,
            "completeness_score": round((detected_count / total_fields) * 100, 1),
        },
    }

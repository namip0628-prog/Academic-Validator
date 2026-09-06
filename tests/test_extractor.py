import unittest
from utils.extractor import extract_academic_fields


class TestAcademicExtractor(unittest.TestCase):
    def setUp(self):
        self.sample_marksheet_text = """
        NATIONAL INSTITUTE OF TECHNOLOGY & ADVANCED STUDIES
        Accredited Grade 'A++' | Autonomous University
        OFFICIAL STATEMENT OF MARKS & DEGREE CONFERMENT

        Candidate's Name: Aarav Sharma
        University Seat Number (USN): 1NT20CS045
        Institution / College: Department of Computer Science & Engineering
        Degree & Programme: Bachelor of Technology in Computer Science
        Cumulative Grade Point Average (CGPA): CGPA: 8.85 / 10.0
        Division / Classification: First Class with Distinction
        Date of Issue: 24/07/2024

        Subject Code  Subject Description               Credits  Grade
        CS801         Cryptography and Network Security   4.0     O
        CS802         Blockchain Technologies             4.0     A+
        CS803         Machine Learning                    4.0     O
        """

    def test_extract_academic_fields(self):
        result = extract_academic_fields(self.sample_marksheet_text)
        fields = result["fields"]

        # Student Name
        self.assertEqual(fields["student_name"]["value"], "Aarav Sharma")
        self.assertEqual(fields["student_name"]["confidence"], "high")

        # Student ID / USN
        self.assertEqual(fields["student_id"]["value"], "1NT20CS045")
        self.assertEqual(fields["student_id"]["confidence"], "high")

        # Institution
        self.assertIn("NATIONAL INSTITUTE OF TECHNOLOGY", fields["institution"]["value"])

        # Course / Degree
        self.assertIn("Bachelor of Technology", fields["course"]["value"])

        # Marks / CGPA
        self.assertIn("8.85", fields["marks"]["value"])

        # Date of Issue
        self.assertIn("24/07/2024", fields["date"]["value"])

        # Summary check
        self.assertEqual(result["summary"]["detected_fields"], 6)
        self.assertEqual(result["summary"]["completeness_score"], 100.0)

    def test_alternative_format_extraction(self):
        alt_text = """
        Apex University of Technology
        CERTIFICATE OF MERIT

        This is to certify that Rahul Verma
        Roll No: 2021-BCS-092
        has completed Bachelor of Engineering (Mechanical)
        with First Class with Distinction.
        CGPA: 9.12 / 10.0
        Passing Year: June 2024
        """
        result = extract_academic_fields(alt_text)
        fields = result["fields"]

        self.assertEqual(fields["student_name"]["value"], "Rahul Verma")
        self.assertEqual(fields["student_id"]["value"], "2021-BCS-092")
        self.assertIn("Apex University", fields["institution"]["value"])
        self.assertIn("Bachelor of Engineering", fields["course"]["value"])
        self.assertIn("9.12", fields["marks"]["value"])
        self.assertIn("2024", fields["date"]["value"])


if __name__ == "__main__":
    unittest.main()

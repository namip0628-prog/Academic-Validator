import unittest
import json
import io
import hashlib
from PIL import Image, ImageDraw

from app import app


class TestValidatorAPI(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_index_route(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Academic Document Authenticity Validator", response.data)

    def test_system_status_route(self):
        response = self.client.get("/api/system-status")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("status", data)
        self.assertIn("opencv_version", data)
        self.assertIn("ocr_available", data)
        self.assertIn("blockchain", data)

    def test_blockchain_status_route(self):
        response = self.client.get("/api/blockchain-status")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("mode", data)
        self.assertIn("chain_id", data)

    def test_validate_sample_route(self):
        response = self.client.post("/api/validate-sample")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertEqual(len(data["sha256_hash"]), 64)
        self.assertIn("preprocessing", data)
        self.assertIn("ocr", data)
        self.assertIn("academic_data", data)

    def test_register_and_verify_api_flow(self):
        test_content = b"Candidate: Jane Smith | ID: 1NT20CS088 | Marksheet Final"
        test_hash = hashlib.sha256(test_content).hexdigest()

        # 1. Register
        reg_payload = {
            "document_hash": test_hash,
            "student_name": "Jane Smith",
            "student_id": "1NT20CS088",
            "institution": "National Institute of Technology",
            "course": "B.Tech Computer Science",
            "marks": "CGPA: 9.4 / 10.0",
            "document_name": "jane_transcript.png",
        }
        reg_resp = self.client.post(
            "/api/register",
            data=json.dumps(reg_payload),
            content_type="application/json",
        )
        self.assertEqual(reg_resp.status_code, 200)
        reg_data = json.loads(reg_resp.data)
        self.assertTrue(reg_data["success"])
        record_id = reg_data.get("record_id")

        # 2. Verify with uploaded file having identical content
        img = Image.new("RGB", (200, 50), color=(255, 255, 255))
        buf = io.BytesIO()
        # Ensure identical bytes
        buf.write(test_content)
        buf.seek(0)

        verify_resp = self.client.post(
            "/api/verify",
            data={"document": (buf, "jane_transcript.png")},
            content_type="multipart/form-data",
        )
        self.assertEqual(verify_resp.status_code, 200)
        verify_data = json.loads(verify_resp.data)["verification"]
        self.assertTrue(verify_data["is_authentic"])
        self.assertEqual(verify_data["status"], "AUTHENTIC")
        self.assertEqual(verify_data["student_name"], "Jane Smith")

        # 3. Verify PDF report download
        if record_id:
            pdf_resp = self.client.get(f"/api/download-report/{record_id}")
            self.assertEqual(pdf_resp.status_code, 200)
            self.assertEqual(pdf_resp.content_type, "application/pdf")
            self.assertGreater(len(pdf_resp.data), 1000)

    def test_verify_sample_route(self):
        response = self.client.post("/api/verify-sample")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertIn("verification", data)
        self.assertEqual(len(data["verification"]["document_hash"]), 64)

    def test_audit_history_route(self):
        response = self.client.get("/api/history")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertIsInstance(data["history"], list)


if __name__ == "__main__":
    unittest.main()

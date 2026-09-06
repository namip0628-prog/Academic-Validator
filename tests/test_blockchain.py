import unittest
import hashlib
from utils.blockchain import BlockchainManager


class TestBlockchainVerification(unittest.TestCase):
    def setUp(self):
        self.bm = BlockchainManager()

    def test_blockchain_status(self):
        status = self.bm.get_status()
        self.assertIn("mode", status)
        self.assertIn("chain_id", status)
        self.assertIn("contract_address", status)

    def test_register_and_verify_authentic_document(self):
        # Create unique document hash for this test
        raw_doc = b"Degree Certificate - Student: John Doe - Marks: 92/100"
        doc_hash = hashlib.sha256(raw_doc).hexdigest()

        # 1. Register on Blockchain
        reg_result = self.bm.register_document(
            document_hash_hex=doc_hash,
            student_name="John Doe",
            student_id="1BM20CS099",
            institution="Apex Institute of Technology",
            course="Bachelor of Technology in AI",
            marks="CGPA: 9.2 / 10.0",
        )

        self.assertTrue(reg_result["success"])
        self.assertEqual(reg_result["document_hash"], doc_hash)
        self.assertIn("transaction_hash", reg_result)
        self.assertIn("block_number", reg_result)
        self.assertIn("timestamp", reg_result)

        # 2. Verify Authentic Document
        verify_result = self.bm.verify_document(doc_hash)
        self.assertTrue(verify_result["is_authentic"])
        self.assertEqual(verify_result["status"], "AUTHENTIC")
        self.assertEqual(verify_result["student_name"], "John Doe")
        self.assertEqual(verify_result["student_id"], "1BM20CS099")
        self.assertEqual(verify_result["institution"], "Apex Institute of Technology")
        self.assertEqual(verify_result["course"], "Bachelor of Technology in AI")
        self.assertEqual(verify_result["marks"], "CGPA: 9.2 / 10.0")

    def test_duplicate_registration_prevention(self):
        raw_doc = b"Unique Transcript for Duplicate Test"
        doc_hash = hashlib.sha256(raw_doc).hexdigest()

        res1 = self.bm.register_document(
            document_hash_hex=doc_hash,
            student_name="Duplicate Tester",
            student_id="DUP-001",
            institution="Test University",
            course="B.Sc",
            marks="85%",
        )
        self.assertTrue(res1["success"])

        # Attempt duplicate registration
        res2 = self.bm.register_document(
            document_hash_hex=doc_hash,
            student_name="Duplicate Tester",
            student_id="DUP-001",
            institution="Test University",
            course="B.Sc",
            marks="85%",
        )
        self.assertFalse(res2["success"])
        self.assertIn("already", res2["error"].lower())

    def test_tamper_detection_unregistered_hash(self):
        # Register an original document
        original = b"Original Authentic Marksheet"
        orig_hash = hashlib.sha256(original).hexdigest()

        self.bm.register_document(
            document_hash_hex=orig_hash,
            student_name="Alice Smith",
            student_id="ALICE-100",
            institution="Oxford Tech",
            course="B.E.",
            marks="First Class",
        )

        # Simulating tampering by modifying 1 byte in the document
        tampered = b"Original Authentic Marksheet (Tampered Marks: 99)"
        tampered_hash = hashlib.sha256(tampered).hexdigest()

        verify_result = self.bm.verify_document(tampered_hash)
        self.assertFalse(verify_result["is_authentic"])
        self.assertEqual(verify_result["status"], "INVALID_OR_MODIFIED")
        self.assertIn("No matching document hash", verify_result["status_message"])


if __name__ == "__main__":
    unittest.main()

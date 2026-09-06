import io
import tempfile
import unittest
from pathlib import Path
from utils.hasher import generate_sha256


class TestDocumentHasher(unittest.TestCase):
    def test_sha256_bytes(self):
        sample_data = b"Academic Transcript - John Doe - USN: 1BM20CS045"
        expected = "54378f4a3500aa9cbcc7bfe0f858850a1e3557e4e112d7c5a04a08f516a7071e"
        actual = generate_sha256(sample_data)
        self.assertEqual(len(actual), 64)
        # Re-verifying mathematically with hashlib
        import hashlib
        self.assertEqual(actual, hashlib.sha256(sample_data).hexdigest())

    def test_sha256_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"Degree Certificate Original")
            tmp_path = Path(tmp.name)

        try:
            hash_val = generate_sha256(tmp_path)
            self.assertEqual(len(hash_val), 64)
            self.assertIsInstance(hash_val, str)
        finally:
            tmp_path.unlink()

    def test_sha256_stream(self):
        bio = io.BytesIO(b"Stream content for academic verification")
        h1 = generate_sha256(bio)
        self.assertEqual(len(h1), 64)

    def test_tamper_detection_avalanche_effect(self):
        original = b"Aarav Sharma | Marks: 95/100 | Distinction"
        tampered = b"Aarav Sharma | Marks: 96/100 | Distinction"

        hash_orig = generate_sha256(original)
        hash_tamp = generate_sha256(tampered)

        self.assertNotEqual(hash_orig, hash_tamp)
        # Even a 1-character difference should result in vastly different hex digests
        different_chars = sum(1 for a, b in zip(hash_orig, hash_tamp) if a != b)
        self.assertGreater(different_chars, 30)


if __name__ == "__main__":
    unittest.main()

# coding: utf-8
import unittest
from aacert_core.lib.jws import b64url, hmac_sha256


class TestJWS(unittest.TestCase):
    def test_b64url_strips_padding(self):
        # 'hello' -> 'aGVsbG8=' standard, stripped is 'aGVsbG8'
        encoded = b64url(b"hello")
        self.assertEqual(encoded, "aGVsbG8")
        self.assertNotIn("=", encoded)

    def test_b64url_url_safe_characters(self):
        data = bytes([251, 239])  # standard b64 '+/' -> urlsafe '-_'
        encoded = b64url(data)
        self.assertNotIn("+", encoded)
        self.assertNotIn("/", encoded)

    def test_hmac_sha256_output_length(self):
        key = b"secret_key"
        msg = b"payload_data"
        digest = hmac_sha256(key, msg)
        self.assertEqual(len(digest), 32)


if __name__ == "__main__":
    unittest.main()

# coding: utf-8
import json
import unittest
from aacert_core.lib.eab import build_eab_object, extract_jwk_from_pem, b64url_decode
from tests.conftest import MOCK_JWK, MOCK_PEM_RSA


class TestEAB(unittest.TestCase):
    def setUp(self):
        self.kid = "test_eab_kid_12345"
        self.hmac_key = "aGVsbG8td29ybGQtaG1hYy1rZXktMTIzNDU2Nzg"
        self.new_account_url = "https://acme.zerossl.com/v2/DV90/newAccount"

    def test_build_eab_object_with_jwk_dict(self):
        eab = build_eab_object(
            kid=self.kid,
            hmac_key=self.hmac_key,
            account_key=MOCK_JWK,
            new_account_url=self.new_account_url
        )
        self.assertIn("protected", eab)
        self.assertIn("payload", eab)
        self.assertIn("signature", eab)

        # Verify decoded protected header
        raw_protected = b64url_decode(eab["protected"])
        header = json.loads(raw_protected.decode("utf-8"))
        self.assertEqual(header["alg"], "HS256")
        self.assertEqual(header["kid"], self.kid)
        self.assertEqual(header["url"], self.new_account_url)

        # Verify payload matches JWK
        raw_payload = b64url_decode(eab["payload"])
        payload_jwk = json.loads(raw_payload.decode("utf-8"))
        self.assertEqual(payload_jwk["kty"], "RSA")
        self.assertEqual(payload_jwk["n"], MOCK_JWK["n"])

    def test_extract_jwk_from_pem(self):
        jwk = extract_jwk_from_pem(MOCK_PEM_RSA)
        self.assertEqual(jwk["kty"], "RSA")
        self.assertIn("n", jwk)
        self.assertIn("e", jwk)
        self.assertEqual(jwk["e"], "AQAB")

    def test_build_eab_object_with_pem_string(self):
        eab = build_eab_object(
            kid=self.kid,
            hmac_key=self.hmac_key,
            account_key=MOCK_PEM_RSA,
            new_account_url=self.new_account_url
        )
        self.assertIn("protected", eab)
        self.assertIn("payload", eab)
        self.assertIn("signature", eab)


if __name__ == "__main__":
    unittest.main()

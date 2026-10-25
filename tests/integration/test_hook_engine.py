# coding: utf-8
import unittest
import sys
from unittest.mock import patch
from aacert_core.services.hook_engine import apply_acme_hook


class MockAcmeInstance:
    """Mock aaPanel acme_v2 class instance."""
    def __init__(self, debug=False):
        self._debug = debug
        self._url = "https://acme-v02.api.letsencrypt.org/directory"
        self._mod_index = {True: "Staging", False: "Production"}
        self._apis = None
        self._email = "admin@example.com"
        self._config = {"orders": {}, "account": {}}

    def acme_request(self, url, payload):
        class MockResponse:
            status_code = 201
            headers = {"Location": "https://acme.test/account/12345"}
            text = '{"status": "valid"}'
            def json(self):
                return {"status": "valid"}
        return MockResponse()

    def get_account_key(self):
        from tests.conftest import MOCK_PEM_RSA
        return MOCK_PEM_RSA

    def get_apis(self):
        return {
            "newAccount": f"{self._url}/newAccount",
            "newOrder": f"{self._url}/newOrder",
            "newNonce": f"{self._url}/newNonce"
        }

    def register(self, email=None):
        return "native_kid_url"


class TestHookEngine(unittest.TestCase):
    @patch("aacert_core.services.hook_engine.load_config")
    def test_hook_applied_for_zerossl(self, mock_load_config):
        mock_load_config.return_value = {
            "enabled": True,
            "active_ca": "zerossl",
            "email": "user@domain.com",
            "providers": {
                "zerossl": {
                    "directory_url": "https://acme.zerossl.com/v2/DV90",
                    "staging_url": "https://acme.zerossl.com/v2/DV90",
                    "eab_required": True,
                    "eab_kid": "dummy_kid",
                    "eab_hmac_key": "dummy_hmac",
                    "cert_days": 90
                }
            }
        }

        instance = MockAcmeInstance()
        apply_acme_hook(instance)

        self.assertEqual(instance._url, "https://acme.zerossl.com/v2/DV90")
        self.assertEqual(instance._mod_index[False], "zerossl_Production")
        self.assertEqual(instance._mod_index[True], "zerossl_Staging")
        self.assertIsNone(instance._apis)
        self.assertEqual(instance._email, "user@domain.com")

        # Test custom_register injected with EAB
        kid = instance.register()
        self.assertEqual(kid, "https://acme.test/account/12345")

    @patch("aacert_core.services.hook_engine.load_config")
    def test_hook_bypassed_when_disabled(self, mock_load_config):
        mock_load_config.return_value = {
            "enabled": False,
            "active_ca": "zerossl"
        }

        instance = MockAcmeInstance()
        apply_acme_hook(instance)

        # Should remain standard Let's Encrypt
        self.assertEqual(instance._url, "https://acme-v02.api.letsencrypt.org/directory")
        self.assertEqual(instance._mod_index[False], "Production")


if __name__ == "__main__":
    unittest.main()

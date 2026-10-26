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
        self.requests = []
        self.response_status = 201

    def acme_request(self, url, payload):
        self.requests.append((url, payload))
        class MockResponse:
            def __init__(self, status_code):
                self.status_code = status_code

            headers = {"Location": "https://acme.test/account/12345"}
            text = '{"status": "valid"}'

            def json(self):
                return {"status": "valid"}

        return MockResponse(self.response_status)

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

    @patch("aacert_core.services.hook_engine.load_config")
    def test_ssl_com_uses_eab_from_legacy_config(self, mock_load_config):
        mock_load_config.return_value = {
            "enabled": True,
            "active_ca": "ssl_com",
            "email": "user@domain.com",
            "providers": {
                "ssl_com": {
                    "directory_url": "https://acme.ssl.com/sslcom-dv-rsa",
                    "staging_url": "https://acme-try.ssl.com/sslcom-dv-rsa",
                    "eab_required": False,
                    "maintenance": False,
                    "eab_kid": "test_ssl_account_key",
                    "eab_hmac_key": "c2VjcmV0",
                }
            },
        }

        instance = MockAcmeInstance()
        apply_acme_hook(instance)
        self.assertEqual(instance.register(), "https://acme.test/account/12345")
        self.assertEqual(len(instance.requests), 1)
        url, payload = instance.requests[0]
        self.assertEqual(url, "https://acme.ssl.com/sslcom-dv-rsa/newAccount")
        self.assertIn("externalAccountBinding", payload)

    @patch("aacert_core.services.hook_engine.load_config")
    def test_ssl_com_requires_both_eab_credentials(self, mock_load_config):
        mock_load_config.return_value = {
            "enabled": True,
            "active_ca": "ssl_com",
            "providers": {
                "ssl_com": {
                    "directory_url": "https://acme.ssl.com/sslcom-dv-rsa",
                    "staging_url": "https://acme-try.ssl.com/sslcom-dv-rsa",
                    "eab_required": False,
                    "maintenance": False,
                }
            },
        }

        instance = MockAcmeInstance()
        apply_acme_hook(instance)
        with self.assertRaisesRegex(RuntimeError, "requires both EAB KID and HMAC"):
            instance.register()
        self.assertEqual(instance.requests, [])

    @patch("aacert_core.services.hook_engine.load_config")
    def test_eab_registration_failure_does_not_retry_without_eab(self, mock_load_config):
        mock_load_config.return_value = {
            "enabled": True,
            "active_ca": "ssl_com",
            "providers": {
                "ssl_com": {
                    "eab_kid": "test_ssl_account_key",
                    "eab_hmac_key": "c2VjcmV0",
                    "maintenance": False,
                }
            },
        }

        instance = MockAcmeInstance()
        instance.response_status = 403
        apply_acme_hook(instance)
        with self.assertRaisesRegex(RuntimeError, "registration with EAB failed"):
            instance.register()
        self.assertEqual(len(instance.requests), 1)
        self.assertIn("externalAccountBinding", instance.requests[0][1])

    @patch("aacert_core.services.hook_engine.load_config")
    def test_ssl_com_maintenance_blocks_certificate_issuance(self, mock_load_config):
        mock_load_config.return_value = {
            "enabled": True,
            "active_ca": "ssl_com",
            "providers": {
                "ssl_com": {
                    "maintenance": True,
                    "maintenance_message": "SSL.com is temporarily under maintenance.",
                }
            },
        }

        instance = MockAcmeInstance()
        instance.apply_cert_domain = lambda *args, **kwargs: {
            "status": True,
            "msg": "certificate issued",
        }
        apply_acme_hook(instance)
        result = instance.apply_cert_domain(["site.example"], "dns")

        self.assertFalse(result["status"])
        self.assertEqual(result["msg"], "SSL.com is temporarily under maintenance.")
        self.assertEqual(instance._url, "https://acme-v02.api.letsencrypt.org/directory")
        self.assertEqual(instance.requests, [])


if __name__ == "__main__":
    unittest.main()

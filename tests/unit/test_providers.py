# coding: utf-8
import unittest
from aacert_core.providers.registry import ProviderRegistry


class TestProviders(unittest.TestCase):
    def test_builtin_providers_exist(self):
        builtins = ProviderRegistry.get_builtin_profiles()
        for ca in ["letsencrypt", "zerossl", "google", "ssl_com"]:
            self.assertIn(ca, builtins)

    def test_zerossl_requires_eab(self):
        profile = ProviderRegistry.get_provider("zerossl")
        self.assertIsNotNone(profile)
        self.assertTrue(profile.eab_required)
        self.assertIn("zerossl.com", profile.directory_url)

    def test_letsencrypt_no_eab(self):
        profile = ProviderRegistry.get_provider("letsencrypt")
        self.assertIsNotNone(profile)
        self.assertFalse(profile.eab_required)
        self.assertIn("letsencrypt.org", profile.directory_url)

    def test_ssl_com_requires_eab_even_with_legacy_config(self):
        profile = ProviderRegistry.get_provider(
            "ssl_com",
            {
                "providers": {
                    "ssl_com": {
                        "eab_required": False,
                        "directory_url": "https://acme.ssl.com/sslcom-dv-rsa",
                    }
                }
            },
        )
        self.assertIsNotNone(profile)
        self.assertTrue(profile.eab_required)

    def test_custom_credentials_override(self):
        mock_cfg = {
            "email": "global@example.com",
            "providers": {
                "zerossl": {
                    "eab_kid": "my_custom_kid",
                    "eab_hmac_key": "my_custom_hmac",
                    "email": "zerossl_user@example.com"
                }
            }
        }
        profile = ProviderRegistry.get_provider("zerossl", mock_cfg)
        self.assertEqual(profile.eab_kid, "my_custom_kid")
        self.assertEqual(profile.eab_hmac_key, "my_custom_hmac")
        self.assertEqual(profile.email, "zerossl_user@example.com")


if __name__ == "__main__":
    unittest.main()

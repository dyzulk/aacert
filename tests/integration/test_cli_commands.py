# coding: utf-8
import io
import sys
import unittest
from unittest.mock import patch
from aacert_core.orchestrator import run_cli
from tests.conftest import temp_config_dir


class TestCLICommands(unittest.TestCase):
    def test_help_uses_compact_command_placeholder(self):
        for argv in ([], ["help"]):
            with self.subTest(argv=argv):
                buf = io.StringIO()
                with patch("sys.stdout", buf):
                    code = run_cli(argv)

                self.assertEqual(code, 0)
                output = buf.getvalue()
                self.assertIn("COMMAND ...", output)
                self.assertNotIn("{version,status", output)
                self.assertIn("Show version information", output)

    def test_cli_version(self):
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            code = run_cli(["version"])
        self.assertEqual(code, 0)
        output = buf.getvalue()
        self.assertIn("aacert v", output)

    def test_cli_version_flags(self):
        for argv in (["-v"], ["--version"]):
            with self.subTest(argv=argv):
                buf = io.StringIO()
                with patch("sys.stdout", buf):
                    with self.assertRaises(SystemExit) as exit_info:
                        run_cli(argv)
                self.assertEqual(exit_info.exception.code, 0)
                self.assertIn("aacert v", buf.getvalue())

    def test_help_flag_and_command(self):
        for argv in (["-h"], ["--help"], ["help"]):
            with self.subTest(argv=argv):
                buf = io.StringIO()
                with patch("sys.stdout", buf):
                    if argv == ["help"]:
                        code = run_cli(argv)
                        self.assertEqual(code, 0)
                    else:
                        with self.assertRaises(SystemExit) as exit_info:
                            run_cli(argv)
                        self.assertEqual(exit_info.exception.code, 0)
                self.assertIn("usage: aacert", buf.getvalue())

    def test_invalid_command_arguments_show_targeted_usage(self):
        cases = (
            (["set-ca"], "usage: aacert set-ca", "Run 'aacert set-ca --help'"),
            (["setup"], "usage: aacert setup", "Run 'aacert setup --help'"),
        )
        for argv, usage, suggestion in cases:
            with self.subTest(argv=argv):
                buf = io.StringIO()
                with patch("sys.stdout", buf):
                    with self.assertRaises(SystemExit) as exit_info:
                        run_cli(argv)

                self.assertEqual(exit_info.exception.code, 2)
                output = buf.getvalue()
                self.assertIn("ERROR", output)
                self.assertIn(usage, output)
                self.assertIn(suggestion, output)
                self.assertNotIn("Available commands:", output)

    def test_ssl_com_setup_explains_account_and_pricing_requirements(self):
        config = {
            "enabled": False,
            "active_ca": "letsencrypt",
            "email": "",
            "providers": {
                "letsencrypt": {
                    "name": "Let's Encrypt",
                    "directory_url": "https://acme-v02.api.letsencrypt.org/directory",
                    "staging_url": "https://acme-staging-v02.api.letsencrypt.org/directory",
                    "eab_required": False,
                    "cert_days": 90,
                },
                "ssl_com": {
                    "name": "SSL.com",
                    "directory_url": "https://acme.ssl.com/sslcom-dv-rsa",
                    "staging_url": "https://acme-try.ssl.com/sslcom-dv-rsa",
                    "eab_required": False,
                    "cert_days": 90,
                },
            },
        }
        with temp_config_dir(initial_cfg=config) as (td, cfg_file):
            with patch("aacert_core.storage.config_store.get_config_path", return_value=cfg_file):
                output = io.StringIO()
                with patch("sys.stdout", output):
                    code = run_cli([
                        "setup",
                        "--ca",
                        "ssl_com",
                        "--email",
                        "acme@example.com",
                    ])

        self.assertEqual(code, 0)
        self.assertIn("requires Account/ACME Key and HMAC (EAB) credentials", output.getvalue())
        self.assertIn("Add your SSL.com EAB credentials", output.getvalue())
        self.assertIn("web-account activation", output.getvalue())
        self.assertIn("confirm the selected SSL.com product/order is Free DV ($0)", output.getvalue())

    def test_unknown_ca_provider_lists_available_providers(self):
        with temp_config_dir() as (td, cfg_file):
            with patch("aacert_core.storage.config_store.get_config_path", return_value=cfg_file):
                output = io.StringIO()
                with patch("sys.stdout", output):
                    with self.assertRaises(SystemExit) as exit_info:
                        run_cli(["set-ca", "ssl.com"])

        self.assertEqual(exit_info.exception.code, 1)
        self.assertIn("Unknown CA provider 'ssl.com'", output.getvalue())
        self.assertIn(
            "Available providers: letsencrypt, zerossl, google, ssl_com",
            output.getvalue(),
        )

    def test_cli_status_and_ca_switch(self):
        with temp_config_dir() as (td, cfg_file):
            with patch("aacert_core.storage.config_store.get_config_path", return_value=cfg_file):
                # Test status
                buf = io.StringIO()
                with patch("sys.stdout", buf):
                    code = run_cli(["status"])
                self.assertEqual(code, 0)
                self.assertIn("Active CA Provider", buf.getvalue())

                # Test set-ca zerossl
                buf = io.StringIO()
                with patch("sys.stdout", buf):
                    code = run_cli(["set-ca", "zerossl"])
                self.assertEqual(code, 0)
                self.assertIn("Active CA changed to", buf.getvalue())

                # Test enable
                buf = io.StringIO()
                with patch("sys.stdout", buf):
                    code = run_cli(["enable"])
                self.assertEqual(code, 0)
                self.assertIn("aacert ENABLED", buf.getvalue())

                # Test disable
                buf = io.StringIO()
                with patch("sys.stdout", buf):
                    code = run_cli(["disable"])
                self.assertEqual(code, 0)
                self.assertIn("aacert DISABLED", buf.getvalue())


if __name__ == "__main__":
    unittest.main()

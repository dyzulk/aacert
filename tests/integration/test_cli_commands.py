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

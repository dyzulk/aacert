# coding: utf-8
import os
import json
import tempfile
import unittest
from aacert_core.storage.panel_state import (
    load_panel_config,
    audit_panel_state,
    cleanup_stale_orders,
    create_state_backup,
)


class TestPanelState(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_panel_state_")
        self.state_file = os.path.join(self.temp_dir, "letsencrypt_v2.json")
        self.sample_data = {
            "account": {
                "Production": {
                    "key": "-----BEGIN PRIVATE KEY-----\nMOCK...",
                    "kid": "https://acme.test/acct/1"
                },
                "zerossl_Production": {
                    "key": "-----BEGIN PRIVATE KEY-----\nMOCK...",
                    "kid": "https://acme.zerossl.com/v2/DV90/account/123"
                }
            },
            "apis": {
                "Production": {"directory": {}},
                "zerossl_Production": {"directory": {}}
            },
            "orders": {
                "order_pending_1": {
                    "status": "pending",
                    "domains": ["test.example.com"]
                },
                "order_valid_1": {
                    "status": "valid",
                    "domains": ["done.example.com"]
                }
            }
        }
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.sample_data, f)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_audit_panel_state(self):
        report = audit_panel_state(self.state_file)
        self.assertTrue(report["exists"])
        self.assertTrue(report["readable"])
        self.assertTrue(report["accounts"]["letsencrypt"]["key_present"])
        self.assertTrue(report["accounts"]["zerossl"]["key_present"])
        self.assertFalse(report["accounts"]["google"]["key_present"])
        self.assertEqual(report["total_orders"], 2)
        self.assertEqual(len(report["pending_orders"]), 1)
        self.assertEqual(len(report["valid_orders"]), 1)

    def test_cleanup_stale_orders(self):
        removed, bpath = cleanup_stale_orders(path=self.state_file)
        self.assertEqual(removed, 1)
        self.assertTrue(os.path.exists(bpath))

        # Reload state file and verify only valid order remains
        reloaded = load_panel_config(self.state_file)
        self.assertEqual(len(reloaded["orders"]), 1)
        self.assertIn("order_valid_1", reloaded["orders"])
        self.assertNotIn("order_pending_1", reloaded["orders"])


if __name__ == "__main__":
    unittest.main()

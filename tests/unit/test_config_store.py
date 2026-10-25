# coding: utf-8
import os
import unittest
from aacert_core.storage.config_store import load_config, save_config, get_config_path
from tests.conftest import temp_config_dir


class TestConfigStore(unittest.TestCase):
    def test_get_config_path_finds_existing(self):
        path = get_config_path()
        self.assertTrue(os.path.exists(path), f"Path {path} does not exist")
        self.assertTrue(path.endswith("config.json"))

    def test_atomic_save_and_reload(self):
        with temp_config_dir() as (td, cfg_file):
            test_data = {"enabled": True, "active_ca": "zerossl", "custom_key": 999}
            saved_path = save_config(test_data, target_path=cfg_file)
            self.assertEqual(saved_path, cfg_file)

            import json
            with open(cfg_file, "r", encoding="utf-8") as f:
                reloaded = json.load(f)
            self.assertEqual(reloaded["active_ca"], "zerossl")
            self.assertEqual(reloaded["custom_key"], 999)


if __name__ == "__main__":
    unittest.main()

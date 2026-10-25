# coding: utf-8
import os
import sys
import json
import tempfile

PACKAGE_DIR = os.path.dirname(os.path.realpath(__file__))
# Root of repository or installation folder: 2 levels up from aacert_core/storage
CORE_ROOT = os.path.dirname(PACKAGE_DIR)
SOURCE_ROOT = os.path.dirname(CORE_ROOT)


def get_candidate_paths() -> list:
    """Return prioritized candidate configuration paths."""
    user_home = os.path.expanduser("~")
    return [
        os.path.join(user_home, ".aacert", "config.json"),
        os.path.join(SOURCE_ROOT, "config.json"),
        os.path.join(CORE_ROOT, "config.json")
    ]


def get_config_path() -> str:
    """Locate the active config.json file."""
    for path in get_candidate_paths():
        if os.path.exists(path):
            return path
    # Default to user installation directory if none exists yet
    return os.path.join(os.path.expanduser("~"), ".aacert", "config.json")


def load_config() -> dict:
    """Load configuration dictionary."""
    cfg_path = get_config_path()
    if not os.path.exists(cfg_path):
        raise FileNotFoundError(f"Configuration file not found. Checked: {get_candidate_paths()}")
    with open(cfg_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(cfg: dict, target_path: str = None) -> str:
    """Atomically write configuration to disk."""
    path = target_path or get_config_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)

    dirname, filename = os.path.split(path)
    with tempfile.NamedTemporaryFile("w", dir=dirname, delete=False, encoding="utf-8") as tf:
        json.dump(cfg, tf, indent=2, ensure_ascii=False)
        tf.flush()
        temp_name = tf.name

    os.replace(temp_name, path)
    return path

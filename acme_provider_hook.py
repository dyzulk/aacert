# coding: utf-8
# ====================================================================
# aacert - Custom ACME Provider Hook Proxy for aaPanel
# https://github.com/dyzulk/aacert
# ====================================================================

import os
import sys

HOOK_FILE = os.path.realpath(__file__)
HOOK_DIR = os.path.dirname(HOOK_FILE)
if HOOK_DIR not in sys.path:
    sys.path.insert(0, HOOK_DIR)

from aacert_core.services.hook_engine import apply_acme_hook
from aacert_core.storage.config_store import load_config, get_config_path


def get_config():
    """Backward-compatible helper returning (config, path)."""
    try:
        cfg = load_config()
        return cfg, get_config_path()
    except Exception:
        return None, None


def apply_hook(acme_obj):
    """Intercept acme_v2 instance at runtime."""
    apply_acme_hook(acme_obj)

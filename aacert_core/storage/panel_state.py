# coding: utf-8
import os
import json

PANEL_LETSENCRYPT_FILE = "/www/server/panel/config/letsencrypt_v2.json"


def load_panel_config() -> dict:
    """Read aaPanel's letsencrypt_v2.json if present."""
    if not os.path.exists(PANEL_LETSENCRYPT_FILE):
        return {}
    try:
        with open(PANEL_LETSENCRYPT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def get_registered_accounts() -> dict:
    """Return dictionary of registered accounts per environment namespace."""
    pcfg = load_panel_config()
    return pcfg.get("account", {})

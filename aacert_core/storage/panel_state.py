# coding: utf-8
import os
import json
import time
import shutil
from typing import Dict, Any, Tuple, List

PANEL_LETSENCRYPT_FILE = "/www/server/panel/config/letsencrypt_v2.json"


def load_panel_config(path: str = None) -> dict:
    """Read aaPanel's letsencrypt_v2.json if present."""
    target = path or PANEL_LETSENCRYPT_FILE
    if not os.path.exists(target):
        return {}
    try:
        with open(target, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_panel_config(data: dict, path: str = None) -> None:
    """Save aaPanel's letsencrypt_v2.json safely."""
    target = path or PANEL_LETSENCRYPT_FILE
    with open(target, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def create_state_backup(path: str = None) -> str:
    """Create timestamped backup of letsencrypt_v2.json."""
    src = path or PANEL_LETSENCRYPT_FILE
    if not os.path.exists(src):
        raise FileNotFoundError(f"Source file {src} not found for backup.")
    backup_file = f"{src}.bak_{int(time.time())}"
    shutil.copyfile(src, backup_file)
    return backup_file


def get_registered_accounts(path: str = None) -> dict:
    """Return dictionary of registered accounts per environment namespace."""
    pcfg = load_panel_config(path)
    return pcfg.get("account", {})


def audit_panel_state(path: str = None) -> Dict[str, Any]:
    """Inspect and audit the state of letsencrypt_v2.json."""
    target = path or PANEL_LETSENCRYPT_FILE
    exists = os.path.exists(target)
    readable = os.access(target, os.R_OK) if exists else False
    writable = os.access(target, os.W_OK) if exists else False

    data = load_panel_config(target) if exists else {}
    accounts = data.get("account", {})
    apis = data.get("apis", {})
    orders = data.get("orders", {})

    pending_orders: List[Dict[str, Any]] = []
    valid_orders: List[Dict[str, Any]] = []

    for order_id, order in orders.items():
        status = order.get("status", "unknown")
        domains = order.get("domains", [])
        entry = {
            "id": order_id,
            "status": status,
            "domains": domains,
            "finalize": order.get("finalize"),
            "create_time": order.get("create_time", 0)
        }
        if status == "pending":
            pending_orders.append(entry)
        else:
            valid_orders.append(entry)

    # Status summary of accounts
    account_summary = {
        "letsencrypt": {
            "key_present": "Production" in accounts and bool(accounts["Production"].get("key")),
            "kid": accounts.get("Production", {}).get("kid")
        },
        "zerossl": {
            "key_present": "zerossl_Production" in accounts and bool(accounts["zerossl_Production"].get("key")),
            "kid": accounts.get("zerossl_Production", {}).get("kid")
        },
        "google": {
            "key_present": "google_Production" in accounts and bool(accounts["google_Production"].get("key")),
            "kid": accounts.get("google_Production", {}).get("kid")
        }
    }

    return {
        "file_path": target,
        "exists": exists,
        "readable": readable,
        "writable": writable,
        "accounts": account_summary,
        "apis_cached": list(apis.keys()),
        "total_orders": len(orders),
        "pending_orders": pending_orders,
        "valid_orders": valid_orders
    }


def cleanup_stale_orders(domain: str = None, path: str = None) -> Tuple[int, str]:
    """
    Safely remove pending/orphaned orders.
    Creates backup first, returns (removed_count, backup_path).
    """
    target = path or PANEL_LETSENCRYPT_FILE
    if not os.path.exists(target):
        return 0, ""

    backup_path = create_state_backup(target)
    data = load_panel_config(target)
    orders = data.get("orders", {})

    to_delete = []
    for order_id, order in orders.items():
        if order.get("status") == "pending":
            if not domain or domain in order.get("domains", []):
                to_delete.append(order_id)

    for order_id in to_delete:
        del orders[order_id]

    data["orders"] = orders
    save_panel_config(data, target)
    return len(to_delete), backup_path

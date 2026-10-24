# coding: utf-8
# ====================================================================
# aacert - Custom ACME Provider Hook for aaPanel
# Intercepts acme_v2 at runtime to support ZeroSSL, Google, SSL.com, etc.
# https://github.com/dyzulk/aacert
# ====================================================================

import os
import sys
import json
import time

HOOK_DIR = os.path.dirname(os.path.abspath(__file__))
if HOOK_DIR not in sys.path:
    sys.path.insert(0, HOOK_DIR)

try:
    from eab_helper import build_eab_object
except ImportError:
    try:
        user_home = os.path.expanduser("~")
        aacert_path = os.path.join(user_home, ".aacert")
        if aacert_path not in sys.path:
            sys.path.insert(0, aacert_path)
        from eab_helper import build_eab_object
    except ImportError:
        build_eab_object = None


def get_config():
    """Load configuration from standard locations."""
    user_home = os.path.expanduser("~")
    locations = [
        os.path.join(user_home, ".aacert", "config.json"),
        os.path.join(HOOK_DIR, "config.json"),
        "/www/server/panel/plugin/aacert/config.json",
        "/root/.aacert/config.json"
    ]
    for loc in locations:
        if os.path.exists(loc):
            try:
                with open(loc, "r", encoding="utf-8") as f:
                    return json.load(f), loc
            except Exception:
                pass
    return None, None


def apply_hook(acme_obj):
    """
    Hook into an instance of aaPanel's acme_v2 class.
    
    Safe design:
    - If disabled or error, returns without modifying anything.
    - Namespaces account/apis keys by CA provider to protect Let's Encrypt keys.
    - Handles asynchronous certificate signing (ZeroSSL / Google PKI order polling).
    """
    try:
        config, cfg_path = get_config()
        if not config or not config.get("enabled", False):
            return

        active_ca = config.get("active_ca", "letsencrypt")
        if active_ca == "letsencrypt":
            return

        providers = config.get("providers", {})
        if active_ca not in providers:
            return

        pinfo = providers[active_ca]
        custom_dir_url = pinfo.get("directory_url")
        if not custom_dir_url:
            return

        # 1. Override the ACME directory URL
        acme_obj._url = custom_dir_url

        # 2. Namespace account and apis keys to prevent overriding Let's Encrypt
        acme_obj._account_key = f"acme_account_key_{active_ca}"
        acme_obj._apis = f"acme_apis_{active_ca}"

        # 3. Use provider email if configured
        ca_email = pinfo.get("email") or config.get("email")
        if ca_email:
            acme_obj._email = ca_email

        # 4. Wrap newAccount / register to inject RFC 8555 EAB payload if required
        if pinfo.get("eab_required", False):
            kid = pinfo.get("eab_kid", "").strip()
            hmac_key = pinfo.get("eab_hmac_key", "").strip()

            if kid and hmac_key and build_eab_object:
                original_register = getattr(acme_obj, "register", None)

                def custom_register(email=None):
                    reg_email = email or ca_email or acme_obj._email
                    if not reg_email:
                        reg_email = "admin@" + (acme_obj._domains[0] if getattr(acme_obj, '_domains', None) else "example.com")
                    acme_obj._email = reg_email

                    acme_obj.get_apis()
                    apis = getattr(acme_obj, "_acme_apis", {})
                    new_account_url = apis.get("newAccount")
                    if not new_account_url:
                        if original_register:
                            return original_register(email)
                        return False

                    eab_payload = build_eab_object(
                        kid=kid,
                        hmac_key=hmac_key,
                        account_key=acme_obj.get_account_key(),
                        new_account_url=new_account_url
                    )

                    payload = {
                        "termsOfServiceAgreed": True,
                        "contact": [f"mailto:{reg_email}"],
                        "externalAccountBinding": eab_payload
                    }

                    res = acme_obj.request(new_account_url, payload)
                    if res.status_code in [200, 201]:
                        acme_obj._account = res.json()
                        acme_obj._kid = res.headers.get("Location")
                        return True
                    elif res.status_code == 200 and "already exists" in res.text.lower():
                        return True
                    else:
                        if original_register:
                            return original_register(email)
                        return False

                acme_obj.register = custom_register

        # 5. Handle async order finalization for CAs like ZeroSSL and Google PKI
        original_send_csr = getattr(acme_obj, "send_csr", None)
        if original_send_csr:
            def custom_send_csr(*args, **kwargs):
                res = original_send_csr(*args, **kwargs)
                try:
                    order = getattr(acme_obj, "_order", {})
                    cert_url = order.get("certificate")
                    status = order.get("status")
                    order_url = getattr(acme_obj, "_order_url", None)

                    # Poll until certificate is ready if status is 'processing'
                    if (not cert_url or status == "processing") and order_url:
                        for _ in range(15):
                            time.sleep(3)
                            chk = acme_obj.request(order_url, "")
                            if chk.status_code == 200:
                                updated_order = chk.json()
                                acme_obj._order = updated_order
                                if updated_order.get("certificate"):
                                    break
                                if updated_order.get("status") == "invalid":
                                    break
                except Exception:
                    pass
                return res

            acme_obj.send_csr = custom_send_csr

    except Exception:
        pass

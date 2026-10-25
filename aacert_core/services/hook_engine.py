# coding: utf-8
import time
from aacert_core.storage.config_store import load_config
from aacert_core.providers.registry import ProviderRegistry
from aacert_core.lib.eab import build_eab_object


def apply_acme_hook(acme_obj) -> None:
    """
    Hook into an instance of aaPanel's acme_v2 class.
    
    Safe design:
    - If disabled or error, returns without modifying anything.
    - Namespaces account/apis keys by CA provider to protect Let's Encrypt keys.
    - Handles asynchronous certificate signing (ZeroSSL / Google PKI order polling).
    """
    try:
        config = load_config()
        if not config or not config.get("enabled", False):
            return

        active_ca = config.get("active_ca", "letsencrypt")
        if active_ca == "letsencrypt":
            return

        profile = ProviderRegistry.get_provider(active_ca, config)
        if not profile:
            return

        is_debug = getattr(acme_obj, "_debug", False)
        custom_dir_url = profile.get_active_url(is_debug)
        if not custom_dir_url:
            return

        # 1. Override the ACME directory URL
        acme_obj._url = custom_dir_url

        # 2. Namespace account and apis keys in aaPanel's config dictionary
        # aaPanel indexes accounts and apis using self._mod_index[self._debug]
        acme_obj._mod_index = {
            True: f"{active_ca}_Staging",
            False: f"{active_ca}_Production"
        }

        # Clear cached directory APIs on instance so aaPanel fetches fresh endpoints for this CA
        acme_obj._apis = None

        # 3. Use provider email if configured
        ca_email = profile.email or config.get("email")
        if ca_email:
            acme_obj._email = ca_email

        # 4. Wrap newAccount / register to inject RFC 8555 EAB payload if required
        if profile.eab_required:
            kid = (profile.eab_kid or "").strip()
            hmac_key = (profile.eab_hmac_key or "").strip()

            if kid and hmac_key:
                original_register = getattr(acme_obj, "register", None)

                def custom_register(email=None):
                    reg_email = email or ca_email or getattr(acme_obj, "_email", None)
                    if not reg_email:
                        reg_email = "admin@" + (acme_obj._domains[0] if getattr(acme_obj, '_domains', None) else "example.com")
                    acme_obj._email = reg_email

                    apis = acme_obj.get_apis()
                    new_account_url = apis.get("newAccount") if isinstance(apis, dict) else None
                    if not new_account_url:
                        if original_register:
                            return original_register(email)
                        return None

                    account_key = acme_obj.get_account_key()
                    eab_payload = build_eab_object(
                        kid=kid,
                        hmac_key=hmac_key,
                        account_key=account_key,
                        new_account_url=new_account_url
                    )

                    payload = {
                        "termsOfServiceAgreed": True,
                        "contact": [f"mailto:{reg_email}"],
                        "externalAccountBinding": eab_payload
                    }

                    res = acme_obj.acme_request(new_account_url, payload)
                    if res.status_code in [200, 201]:
                        acme_obj._account = res.json()
                        account_kid = res.headers.get("Location")
                        return account_kid
                    elif res.status_code == 200 and "already exists" in res.text.lower():
                        return res.headers.get("Location")
                    elif res.status_code == 409 or "already exists" in res.text.lower():
                        # Account already exists; retrieve existing account URL
                        ex_res = acme_obj.acme_request(new_account_url, {"onlyReturnExisting": True})
                        if ex_res.status_code in [200, 201]:
                            return ex_res.headers.get("Location")

                    if original_register:
                        return original_register(email)
                    return None

                acme_obj.register = custom_register

        # 5. Handle async order finalization for CAs like ZeroSSL and Google PKI
        original_send_csr = getattr(acme_obj, "send_csr", None)
        if original_send_csr:
            def custom_send_csr(index, *args, **kwargs):
                certificate_url = original_send_csr(index, *args, **kwargs)
                try:
                    order_info = getattr(acme_obj, "_config", {}).get('orders', {}).get(index, {})
                    order_finalize_url = order_info.get('finalize')
                    if not certificate_url and order_finalize_url:
                        order_url = order_finalize_url.rsplit('/finalize', 1)[0]
                        for _ in range(15):
                            time.sleep(3)
                            chk = acme_obj.acme_request(order_url, "")
                            if chk.status_code == 200:
                                updated_order = chk.json()
                                if updated_order.get("certificate"):
                                    cert_url = updated_order.get("certificate")
                                    acme_obj._config['orders'][index]['certificate_url'] = cert_url
                                    acme_obj.save_config()
                                    return cert_url
                                if updated_order.get("status") == "invalid":
                                    break
                except Exception:
                    pass
                return certificate_url

            acme_obj.send_csr = custom_send_csr

        # 6. Intercept get_error to bypass aaPanel's string.find() truthy bug
        original_get_error = getattr(acme_obj, "get_error", None)
        if original_get_error:
            def custom_get_error(error):
                err_str = str(error)
                ret = original_get_error(error)
                # aaPanel line 1192 has 'elif error.find("too many failed authorizations recently"):' without '!= -1'.
                # In Python, string.find() returns -1 on non-match, which evaluates to True.
                # If the returned message claims rate limit but the error doesn't contain that substring, return real error.
                if "more than 5 failed orders within 1 hour" in str(ret).lower() and \
                   "too many failed authorizations recently" not in err_str:
                    return err_str
                return ret

            acme_obj.get_error = custom_get_error

    except Exception:
        pass

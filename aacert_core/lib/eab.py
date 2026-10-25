# coding: utf-8
# ====================================================================
# RFC 8555 External Account Binding (EAB) Helper
# ====================================================================

import json
import binascii
from aacert_core.lib.jws import b64url, hmac_sha256


def b64url_decode(s: str) -> bytes:
    """Decode base64 / base64url string with padding handling."""
    import base64
    s = s.strip().replace("-", "+").replace("_", "/")
    rem = len(s) % 4
    if rem > 0:
        s += "=" * (4 - rem)
    return base64.b64decode(s)


def extract_jwk_from_pem(pem_str: str) -> dict:
    """Extract public key JWK dict from PEM private or public key."""
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization

    key_bytes = pem_str.encode("utf-8") if isinstance(pem_str, str) else pem_str
    try:
        priv = serialization.load_pem_private_key(key_bytes, password=None, backend=default_backend())
        pub_numbers = priv.public_key().public_numbers()
    except Exception:
        pub = serialization.load_pem_public_key(key_bytes, backend=default_backend())
        pub_numbers = pub.public_numbers()

    exp_hex = f"{pub_numbers.e:x}"
    if len(exp_hex) % 2:
        exp_hex = "0" + exp_hex
    mod_hex = f"{pub_numbers.n:x}"
    if len(mod_hex) % 2:
        mod_hex = "0" + mod_hex

    return {
        "kty": "RSA",
        "e": b64url(binascii.unhexlify(exp_hex)),
        "n": b64url(binascii.unhexlify(mod_hex))
    }


def build_eab_object(kid: str = None, hmac_key: str = None, account_key = None, new_account_url: str = None, **kwargs) -> dict:
    """
    Build RFC 8555 Section 7.3.4 externalAccountBinding object.
    
    Accepts flexible keyword args for backward compatibility:
    - kid / eab_kid
    - hmac_key / eab_hmac_key
    - account_key (JWK dict, PEM string, or acme_v2 object) / account_jwk
    - new_account_url / url
    """
    # 1. Resolve arguments
    eab_kid = (kid or kwargs.get("eab_kid", "")).strip()
    eab_hmac = (hmac_key or kwargs.get("eab_hmac_key", "")).strip()
    url = (new_account_url or kwargs.get("url", "")).strip()

    acc = account_key if account_key is not None else kwargs.get("account_jwk")

    # 2. Extract JWK
    if isinstance(acc, dict) and "kty" in acc:
        account_jwk = acc
    elif hasattr(acc, "get_acme_header"):
        account_jwk = acc.get_acme_header("GET_THUMBPRINT")["jwk"]
    elif isinstance(acc, str) and ("BEGIN" in acc or "PRIVATE" in acc or "PUBLIC" in acc):
        account_jwk = extract_jwk_from_pem(acc)
    else:
        raise ValueError("Invalid account key or JWK provided to build_eab_object")

    # 3. Protected Header
    protected_dict = {
        "alg": "HS256",
        "kid": eab_kid,
        "url": url
    }
    protected_b64 = b64url(json.dumps(protected_dict, separators=(",", ":"), sort_keys=True).encode("utf-8"))

    # 4. Payload (Public key JWK)
    payload_b64 = b64url(json.dumps(account_jwk, separators=(",", ":"), sort_keys=True).encode("utf-8"))

    # 5. HMAC Signature
    signing_input = f"{protected_b64}.{payload_b64}".encode("ascii")
    raw_hmac_key = b64url_decode(eab_hmac)
    sig_b64 = b64url(hmac_sha256(raw_hmac_key, signing_input))

    return {
        "protected": protected_b64,
        "payload": payload_b64,
        "signature": sig_b64
    }

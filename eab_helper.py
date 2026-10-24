# coding: utf-8
# ====================================================================
# RFC 8555 External Account Binding (EAB) Helper
# Used for ZeroSSL, Google Public CA, and other ACME servers requiring EAB
# ====================================================================

import base64
import hashlib
import hmac
import json


def b64url_encode(data: bytes) -> str:
    """Encode bytes to base64url without padding."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def b64url_decode(s: str) -> bytes:
    """Decode base64url string with optional padding handling."""
    s = s.strip()
    # Normalize standard base64 if needed
    s = s.replace("-", "+").replace("_", "/")
    rem = len(s) % 4
    if rem > 0:
        s += "=" * (4 - rem)
    return base64.b64decode(s)


def build_eab_object(account_jwk: dict, eab_kid: str, eab_hmac_key: str, new_account_url: str) -> dict:
    """
    Build RFC 8555 Section 7.3.4 externalAccountBinding object.
    
    Args:
        account_jwk: Public key JWK dictionary (kty, n, e).
        eab_kid: Key identifier provided by CA (e.g. Google or ZeroSSL).
        eab_hmac_key: Base64/Base64url encoded HMAC key provided by CA.
        new_account_url: The newAccount endpoint URL from directory.
        
    Returns:
        dict with protected, payload, signature strings.
    """
    # 1. Protected Header
    protected_dict = {
        "alg": "HS256",
        "kid": eab_kid.strip(),
        "url": new_account_url.strip()
    }
    protected_bytes = json.dumps(protected_dict, separators=(",", ":"), sort_keys=True).encode("utf-8")
    protected_b64 = b64url_encode(protected_bytes)

    # 2. Payload (Account Public Key in JWK format)
    payload_bytes = json.dumps(account_jwk, separators=(",", ":"), sort_keys=True).encode("utf-8")
    payload_b64 = b64url_encode(payload_bytes)

    # 3. Signature
    signing_input = "{0}.{1}".format(protected_b64, payload_b64).encode("ascii")
    raw_key = b64url_decode(eab_hmac_key)
    sig_bytes = hmac.new(raw_key, signing_input, hashlib.sha256).digest()
    sig_b64 = b64url_encode(sig_bytes)

    return {
        "protected": protected_b64,
        "payload": payload_b64,
        "signature": sig_b64
    }

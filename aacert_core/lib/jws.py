# coding: utf-8
import base64
import hmac
import hashlib


def b64url(data: bytes) -> str:
    """Base64URL encode without trailing padding '='."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def hmac_sha256(key: bytes, message: bytes) -> bytes:
    """Compute HMAC-SHA256 signature."""
    return hmac.new(key, message, hashlib.sha256).digest()

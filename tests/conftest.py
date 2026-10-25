# coding: utf-8
import os
import sys
import tempfile
import shutil
from contextlib import contextmanager

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

MOCK_JWK = {
    "kty": "RSA",
    "n": "0vx7agoebGcQSuuPiPSXZzxOdBI47qKW3950lsCES5E",
    "e": "AQAB"
}


def _generate_valid_mock_rsa_pem() -> str:
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode("utf-8")


MOCK_PEM_RSA = _generate_valid_mock_rsa_pem()


@contextmanager
def temp_config_dir(initial_cfg=None):
    """Create a temporary sandbox containing a valid config.json."""
    temp_dir = tempfile.mkdtemp(prefix="aacert_test_")
    cfg_file = os.path.join(temp_dir, "config.json")
    import json
    data = initial_cfg or {
        "enabled": False,
        "active_ca": "letsencrypt",
        "email": "test@example.com",
        "providers": {
            "letsencrypt": {
                "name": "Let's Encrypt",
                "directory_url": "https://acme-v02.api.letsencrypt.org/directory",
                "staging_url": "https://acme-staging-v02.api.letsencrypt.org/directory",
                "eab_required": False,
                "cert_days": 90
            },
            "zerossl": {
                "name": "ZeroSSL",
                "directory_url": "https://acme.zerossl.com/v2/DV90",
                "staging_url": "https://acme.zerossl.com/v2/DV90",
                "eab_required": True,
                "eab_kid": "test_kid",
                "eab_hmac_key": "test_hmac",
                "cert_days": 90
            }
        }
    }
    with open(cfg_file, "w", encoding="utf-8") as f:
        json.dump(data, f)

    try:
        yield temp_dir, cfg_file
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

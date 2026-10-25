# coding: utf-8
from aacert_core.providers.base import ProviderProfile

ZEROSSL_PROFILE = ProviderProfile(
    id="zerossl",
    name="ZeroSSL",
    directory_url="https://acme.zerossl.com/v2/DV90",
    staging_url="https://acme.zerossl.com/v2/DV90",
    eab_required=True,
    cert_days=90,
    description="Free 90-day DV certificate. EAB KID and HMAC Key required."
)

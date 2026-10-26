# coding: utf-8
from aacert_core.providers.base import ProviderProfile

SSL_COM_PROFILE = ProviderProfile(
    id="ssl_com",
    name="SSL.com",
    directory_url="https://acme.ssl.com/sslcom-dv-rsa",
    staging_url="https://acme-try.ssl.com/sslcom-dv-rsa",
    eab_required=True,
    cert_days=90,
    description="SSL.com DV certificate. Account/ACME Key and HMAC credentials are required."
)

# coding: utf-8
from aacert_core.providers.base import ProviderProfile

SSL_COM_PROFILE = ProviderProfile(
    id="ssl_com",
    name="SSL.com",
    directory_url="https://acme.ssl.com/sslcom-dv-rsa",
    staging_url="https://acme-try.ssl.com/sslcom-dv-rsa",
    eab_required=True,
    cert_days=90,
    description="SSL.com ACME issuance is temporarily paused while authorization delays are investigated. EAB credentials remain configurable.",
    maintenance=True,
    maintenance_message=(
        "SSL.com issuance is temporarily paused while ACME authorization delays "
        "are investigated. Choose another provider or aaPanel's native Let's Encrypt."
    ),
)

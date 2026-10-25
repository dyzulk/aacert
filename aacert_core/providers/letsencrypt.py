# coding: utf-8
from aacert_core.providers.base import ProviderProfile

LETSENCRYPT_PROFILE = ProviderProfile(
    id="letsencrypt",
    name="Let's Encrypt",
    directory_url="https://acme-v02.api.letsencrypt.org/directory",
    staging_url="https://acme-staging-v02.api.letsencrypt.org/directory",
    eab_required=False,
    cert_days=90,
    description="Default free CA (90 days). No EAB required."
)

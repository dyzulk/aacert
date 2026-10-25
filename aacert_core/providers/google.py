# coding: utf-8
from aacert_core.providers.base import ProviderProfile

GOOGLE_PROFILE = ProviderProfile(
    id="google",
    name="Google Public CA",
    directory_url="https://dv.acme-v02.api.pki.goog/directory",
    staging_url="https://dv.acme-v02.test-api.pki.goog/directory",
    eab_required=True,
    cert_days=90,
    description="Google Trust Services (90 days). Free EAB credentials from Google Cloud."
)

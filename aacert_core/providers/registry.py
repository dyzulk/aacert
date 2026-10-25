# coding: utf-8
from typing import Dict, Optional
from aacert_core.providers.base import ProviderProfile
from aacert_core.providers.letsencrypt import LETSENCRYPT_PROFILE
from aacert_core.providers.zerossl import ZEROSSL_PROFILE
from aacert_core.providers.google import GOOGLE_PROFILE
from aacert_core.providers.ssl_com import SSL_COM_PROFILE

_BUILTIN_PROFILES: Dict[str, ProviderProfile] = {
    "letsencrypt": LETSENCRYPT_PROFILE,
    "zerossl": ZEROSSL_PROFILE,
    "google": GOOGLE_PROFILE,
    "ssl_com": SSL_COM_PROFILE
}


class ProviderRegistry:
    @classmethod
    def get_builtin_profiles(cls) -> Dict[str, ProviderProfile]:
        return dict(_BUILTIN_PROFILES)

    @classmethod
    def get_provider(cls, ca_id: str, config: dict = None) -> Optional[ProviderProfile]:
        ca_id = ca_id.lower().strip()
        profile = _BUILTIN_PROFILES.get(ca_id)

        if not profile and config:
            pinfo = config.get("providers", {}).get(ca_id)
            if pinfo:
                profile = ProviderProfile(
                    id=ca_id,
                    name=pinfo.get("name", ca_id),
                    directory_url=pinfo.get("directory_url", ""),
                    staging_url=pinfo.get("staging_url", ""),
                    eab_required=pinfo.get("eab_required", False),
                    cert_days=pinfo.get("cert_days", 90),
                    description=pinfo.get("description", "")
                )

        if profile and config:
            pinfo = config.get("providers", {}).get(ca_id, {})
            # Merge user custom credentials
            return ProviderProfile(
                id=profile.id,
                name=pinfo.get("name", profile.name),
                directory_url=pinfo.get("directory_url", profile.directory_url),
                staging_url=pinfo.get("staging_url", profile.staging_url),
                eab_required=pinfo.get("eab_required", profile.eab_required),
                cert_days=pinfo.get("cert_days", profile.cert_days),
                description=pinfo.get("description", profile.description),
                eab_kid=pinfo.get("eab_kid"),
                eab_hmac_key=pinfo.get("eab_hmac_key"),
                email=pinfo.get("email") or config.get("email")
            )

        return profile

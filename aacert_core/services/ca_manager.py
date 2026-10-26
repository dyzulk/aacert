# coding: utf-8
from typing import Dict, Any
from aacert_core.storage.config_store import load_config, save_config
from aacert_core.providers.registry import ProviderRegistry
from aacert_core.services.patch_manager import PatchManager


class CAManager:
    @staticmethod
    def _unknown_provider_error(ca_id: str, cfg: dict) -> ValueError:
        available = ", ".join(ProviderRegistry.get_available_provider_ids(cfg))
        return ValueError(
            f"Unknown CA provider '{ca_id}'. Available providers: {available}"
        )

    @staticmethod
    def get_status() -> Dict[str, Any]:
        cfg = load_config()
        active_ca = cfg.get("active_ca", "letsencrypt")
        profile = ProviderRegistry.get_provider(active_ca, cfg)
        patch_installed = PatchManager.is_patch_installed()

        return {
            "enabled": cfg.get("enabled", False),
            "patch_installed": patch_installed,
            "active_ca": active_ca,
            "profile": profile,
            "config": cfg,
            "email": (profile.email if profile else None) or cfg.get("email")
        }

    @staticmethod
    def set_active_ca(ca_id: str) -> Dict[str, Any]:
        cfg = load_config()
        ca_id = ca_id.lower().strip()
        profile = ProviderRegistry.get_provider(ca_id, cfg)
        if not profile:
            raise CAManager._unknown_provider_error(ca_id, cfg)

        cfg["active_ca"] = ca_id
        save_config(cfg)
        return {"active_ca": ca_id, "profile": profile}

    @staticmethod
    def enable() -> None:
        cfg = load_config()
        cfg["enabled"] = True
        save_config(cfg)

    @staticmethod
    def disable() -> None:
        cfg = load_config()
        cfg["enabled"] = False
        save_config(cfg)

    @staticmethod
    def update_credentials(ca_id: str, email: str = None, kid: str = None, hmac: str = None, enable: bool = False) -> None:
        cfg = load_config()
        ca_id = ca_id.lower().strip()
        if ca_id not in cfg.get("providers", {}):
            raise CAManager._unknown_provider_error(ca_id, cfg)

        cfg["active_ca"] = ca_id
        pinfo = cfg["providers"][ca_id]

        if email:
            pinfo["email"] = email.strip()
            cfg["email"] = email.strip()

        if kid:
            pinfo["eab_kid"] = kid.strip()

        if hmac:
            pinfo["eab_hmac_key"] = hmac.strip()

        if enable:
            cfg["enabled"] = True

        save_config(cfg)

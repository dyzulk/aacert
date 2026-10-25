# coding: utf-8
import os

PANEL_ACME_V2 = "/www/server/panel/class/acme_v2.py"
HOOK_TAG = "# [AACERT_HOOK_START]"
LEGACY_HOOK_TAG = "# [ACME_MANAGER_HOOK_START]"


class PatchManager:
    @staticmethod
    def is_patch_installed() -> bool:
        if not os.path.exists(PANEL_ACME_V2):
            return False
        try:
            with open(PANEL_ACME_V2, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                return (HOOK_TAG in content) or (LEGACY_HOOK_TAG in content)
        except Exception:
            return False

    @staticmethod
    def get_patch_status() -> str:
        return "INSTALLED" if PatchManager.is_patch_installed() else "NOT_INSTALLED"

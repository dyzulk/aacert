# coding: utf-8
import sys

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_banner(version: str) -> None:
    print("=" * 60)
    print(f"  aacert v{version} - Multi-CA ACME Manager for aaPanel")
    print("=" * 60)


def print_status(status_info: dict, version: str) -> None:
    print_banner(version)

    enabled = status_info["enabled"]
    status_label = f"[{GREEN}ENABLED{RESET}]" if enabled else f"[{RED}DISABLED{RESET}]"
    print(f" Module Status       : {status_label}")

    patch_ok = status_info["patch_installed"]
    patch_label = f"[{GREEN}INSTALLED{RESET}]" if patch_ok else f"[{YELLOW}NOT INSTALLED{RESET}] (Run: aacert install)"
    print(f" aaPanel Hook Patch  : {patch_label}")

    email = status_info.get("email") or "(not configured)"
    print(f" Account Email       : {email}")

    profile = status_info.get("profile")
    active_ca = status_info.get("active_ca")
    ca_name = profile.name if profile else active_ca
    print(f" Active CA Provider  : {CYAN}{ca_name}{RESET} (ID: {active_ca})")
    print(f" Directory URL       : {profile.directory_url if profile else 'N/A'}")
    print(f" Cert Validity Period: ~{profile.cert_days if profile else 90} days")

    eab_req = profile.eab_required if profile else False
    print(f" Requires EAB Key    : {'YES' if eab_req else 'NO'}")
    if eab_req and profile:
        kid = (profile.eab_kid or "").strip()
        hmac_k = (profile.eab_hmac_key or "").strip()
        has_kid = f"{GREEN}CONFIGURED{RESET} ({kid[:6]}...{kid[-4:]})" if kid else f"{RED}MISSING{RESET}"
        has_hmac = f"{GREEN}CONFIGURED{RESET} (Hidden)" if hmac_k else f"{RED}MISSING{RESET}"
        print(f"   -> EAB KID        : {has_kid}")
        print(f"   -> EAB HMAC       : {has_hmac}")

    print("-" * 60)
    print(" Available Providers:")
    from aacert_core.providers.registry import ProviderRegistry
    cfg = status_info.get("config", {})
    all_providers = cfg.get("providers", {})
    for key, p in all_providers.items():
        marker = "-> " if key == active_ca else "   "
        provider = ProviderRegistry.get_provider(key, cfg)
        eab_str = " (EAB required)" if provider and provider.eab_required else " (No EAB)"
        print(f"  {marker}{key:<12} : {p.get('name')}{eab_str} [{p.get('cert_days')}d]")
    print("=" * 60)

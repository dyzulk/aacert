# coding: utf-8
import os
import sys
import subprocess
from aacert_core import __version__
from aacert_core.services.ca_manager import CAManager
from aacert_core.services.network_service import NetworkService
from aacert_core.services.patch_manager import PatchManager
from aacert_core.cli.ui import print_status, GREEN, RED, YELLOW, CYAN, RESET
from aacert_core.storage.config_store import SOURCE_ROOT


def _print_ssl_com_note(ca_id):
    if ca_id.strip().lower() == "ssl_com":
        print(
            f"[{YELLOW}NOTE{RESET}] SSL.com does not require EAB, but may require "
            "you to activate your SSL.com web account and complete its billing "
            "profile before ACME account registration or issuance."
        )
        print(
            "       This does not mean the certificate is free: confirm the "
            "selected SSL.com product/order is Free DV ($0) in its portal."
        )


def handle_version(args):
    print(f"aacert v{__version__}")
    print("Multi-CA ACME Manager for aaPanel")
    print("https://github.com/dyzulk/aacert")


def handle_status(args):
    status_info = CAManager.get_status()
    print_status(status_info, __version__)


def handle_setup(args):
    try:
        CAManager.update_credentials(
            ca_id=args.ca,
            email=args.email,
            kid=args.kid,
            hmac=args.hmac,
            enable=args.enable
        )
        status_info = CAManager.get_status()
        profile = status_info.get("profile")
        ca_name = profile.name if profile else args.ca
        print(f"[{GREEN}OK{RESET}] Provider '{ca_name}' successfully configured.")
        _print_ssl_com_note(args.ca)
        if status_info.get("enabled"):
            print(f"[{GREEN}OK{RESET}] aacert is now ENABLED.")
        else:
            print(f"[{YELLOW}INFO{RESET}] Module is currently DISABLED. Pass --enable or run: aacert enable")
    except Exception as e:
        print(f"[{RED}ERROR{RESET}] {str(e)}")
        sys.exit(1)


def handle_enable(args):
    CAManager.enable()
    status_info = CAManager.get_status()
    print(f"[{GREEN}OK{RESET}] aacert ENABLED.")
    print(f"Active provider is: {status_info.get('active_ca')}")
    if not status_info.get("patch_installed"):
        print(f"[{YELLOW}NOTE{RESET}] Hook patch not installed. Run: aacert install")


def handle_disable(args):
    CAManager.disable()
    print(f"[{GREEN}OK{RESET}] aacert DISABLED.")
    print("aaPanel will now use native Let's Encrypt default.")


def handle_set_ca(args):
    try:
        res = CAManager.set_active_ca(args.ca_name)
        profile = res.get("profile")
        ca_name = profile.name if profile else args.ca_name
        print(f"[{GREEN}OK{RESET}] Active CA changed to: {CYAN}{ca_name}{RESET} ({args.ca_name})")
        _print_ssl_com_note(args.ca_name)
        if profile and profile.eab_required:
            kid = (profile.eab_kid or "").strip()
            hmac_k = (profile.eab_hmac_key or "").strip()
            if not kid or not hmac_k:
                print(f"[{YELLOW}WARNING{RESET}] This provider requires EAB credentials. Set them with:")
                print(f"  aacert setup --ca {args.ca_name} --kid <KID> --hmac <HMAC>")
    except Exception as e:
        print(f"[{RED}ERROR{RESET}] {str(e)}")
        sys.exit(1)


def handle_set_eab(args):
    try:
        CAManager.update_credentials(
            ca_id=args.ca_name,
            email=args.email,
            kid=args.kid,
            hmac=args.hmac
        )
        print(f"[{GREEN}OK{RESET}] EAB credentials updated for provider '{args.ca_name}'.")
    except Exception as e:
        print(f"[{RED}ERROR{RESET}] {str(e)}")
        sys.exit(1)


def handle_test(args):
    status_info = CAManager.get_status()
    ca_id = (args.ca_name or status_info.get("active_ca", "letsencrypt")).lower().strip()
    from aacert_core.providers.registry import ProviderRegistry
    profile = ProviderRegistry.get_provider(ca_id, status_info.get("config"))

    if not profile:
        available = ", ".join(
            ProviderRegistry.get_available_provider_ids(status_info.get("config"))
        )
        print(
            f"[{RED}ERROR{RESET}] Unknown CA provider '{ca_id}'. "
            f"Available providers: {available}"
        )
        sys.exit(1)

    url = profile.directory_url
    print(f"Testing connection to {profile.name}...")
    print(f"URL: {url}")

    try:
        res = NetworkService.test_directory(url, user_agent=f"aacert/{__version__}")
        print(f"[{GREEN}SUCCESS{RESET}] HTTP {res['status']}")
        for ep, ep_url in res.get("endpoints", {}).items():
            if ep_url:
                print(f"  {ep:<10} : {ep_url}")
    except Exception as e:
        print(f"[{RED}FAILED{RESET}] {str(e)}")
        sys.exit(1)


def handle_install(args):
    script = os.path.join(SOURCE_ROOT, "install.sh")
    if not os.path.exists(script):
        # Fallback to local
        script = os.path.expanduser("~/.aacert/install.sh")
    if not os.path.exists(script):
        print(f"[!] install.sh not found at {script}")
        sys.exit(1)
    subprocess.run(["bash", script], check=True)


def handle_uninstall(args):
    script = os.path.join(SOURCE_ROOT, "uninstall.sh")
    if not os.path.exists(script):
        script = os.path.expanduser("~/.aacert/uninstall.sh")
    if not os.path.exists(script):
        print(f"[!] uninstall.sh not found at {script}")
        sys.exit(1)
    subprocess.run(["bash", script], check=True)


def handle_doctor(args):
    from aacert_core.storage.panel_state import audit_panel_state, cleanup_stale_orders
    report = audit_panel_state()

    print("=" * 60)
    print("  aacert Doctor - aaPanel ACME Integrity Report")
    print("=" * 60)

    exists_label = f"[{GREEN}EXISTS{RESET}]" if report["exists"] else f"[{RED}NOT FOUND{RESET}]"
    print(f" State File Path   : {report['file_path']}")
    print(f" File Status       : {exists_label}")
    if report["exists"]:
        r_str = f"{GREEN}YES{RESET}" if report["readable"] else f"{RED}NO{RESET}"
        w_str = f"{GREEN}YES{RESET}" if report["writable"] else f"{RED}NO{RESET}"
        print(f" File Permissions  : Read={r_str}, Write={w_str}")

    print("-" * 60)
    print(" Registered CA Accounts:")
    for ca_id, acc in report.get("accounts", {}).items():
        if acc.get("key_present") and acc.get("kid"):
            kid = acc.get("kid")
            masked_kid = f"{kid[:35]}...{kid[-10:]}" if len(kid) > 50 else kid
            print(f"  - {ca_id:<14} : [{GREEN}REGISTERED{RESET}] ({masked_kid})")
        elif acc.get("key_present"):
            print(f"  - {ca_id:<14} : [{YELLOW}KEY PRESENT, NO KID{RESET}]")
        else:
            print(f"  - {ca_id:<14} : [{RED}NOT REGISTERED{RESET}] (Will register on first issuance)")

    print("-" * 60)
    print(f" Order Status (Total: {report['total_orders']}):")
    print(f"  - Completed/Valid: {len(report['valid_orders'])}")
    print(f"  - Stale/Pending  : {len(report['pending_orders'])}")
    for p in report["pending_orders"]:
        print(f"      * Order ID {p['id'][:8]}... | Domains: {p['domains']}")

    if getattr(args, "clean_pending", False):
        if report["pending_orders"]:
            removed, bpath = cleanup_stale_orders()
            print("-" * 60)
            print(f"[{GREEN}CLEANED{RESET}] Purged {removed} stale pending orders.")
            print(f"Backup created at: {bpath}")
        else:
            print("-" * 60)
            print(f"[{GREEN}OK{RESET}] No stale pending orders found to clean.")

    print("=" * 60)

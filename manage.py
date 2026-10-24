#!/usr/bin/env python3
# coding: utf-8
# ====================================================================
# aacert - Multi-CA ACME Manager for aaPanel
# CLI Tool
# https://github.com/dyzulk/aacert
# ====================================================================

import os
import sys
import json
import argparse
import urllib.request
import ssl

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
PANEL_ACME_V2 = "/www/server/panel/class/acme_v2.py"
HOOK_TAG = "# [ACME_MANAGER_HOOK_START]"
VERSION = "1.0.0"


def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"[!] Error: Configuration file not found at {CONFIG_FILE}")
        sys.exit(1)
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def is_patch_installed():
    if not os.path.exists(PANEL_ACME_V2):
        return False
    try:
        with open(PANEL_ACME_V2, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            return HOOK_TAG in content
    except Exception:
        return False


def cmd_version(args):
    print(f"aacert v{VERSION}")
    print("Multi-CA ACME Manager for aaPanel")
    print("https://github.com/dyzulk/aacert")


def cmd_status(args):
    cfg = load_config()
    enabled = cfg.get("enabled", False)
    active_ca = cfg.get("active_ca", "letsencrypt")
    providers = cfg.get("providers", {})
    pinfo = providers.get(active_ca, {})
    patch_ok = is_patch_installed()

    print("=" * 60)
    print(f"  aacert v{VERSION} - Multi-CA ACME Manager for aaPanel")
    print("=" * 60)

    status_label = "[\033[92mENABLED\033[0m]" if enabled else "[\033[91mDISABLED\033[0m]"
    print(f" Module Status       : {status_label}")

    patch_label = "[\033[92mINSTALLED\033[0m]" if patch_ok else "[\033[93mNOT INSTALLED\033[0m] (Run: aacert install)"
    print(f" aaPanel Hook Patch  : {patch_label}")

    email = pinfo.get("email") or cfg.get("email") or "(not configured)"
    print(f" Account Email       : {email}")
    print(f" Active CA Provider  : \033[96m{pinfo.get('name', active_ca)}\033[0m (ID: {active_ca})")
    print(f" Directory URL       : {pinfo.get('directory_url', 'N/A')}")
    print(f" Cert Validity Period: ~{pinfo.get('cert_days', 90)} days")

    eab_req = pinfo.get("eab_required", False)
    print(f" Requires EAB Key    : {'YES' if eab_req else 'NO'}")
    if eab_req:
        kid = pinfo.get("eab_kid", "").strip()
        hmac_k = pinfo.get("eab_hmac_key", "").strip()
        has_kid = f"\033[92mCONFIGURED\033[0m ({kid[:6]}...{kid[-4:]})" if kid else "\033[91mMISSING\033[0m"
        has_hmac = "\033[92mCONFIGURED\033[0m (Hidden)" if hmac_k else "\033[91mMISSING\033[0m"
        print(f"   -> EAB KID        : {has_kid}")
        print(f"   -> EAB HMAC       : {has_hmac}")

    print("-" * 60)
    print(" Available Providers:")
    for key, p in providers.items():
        marker = "-> " if key == active_ca else "   "
        eab_str = " (EAB required)" if p.get("eab_required") else " (No EAB)"
        print(f"  {marker}{key:<12} : {p.get('name')}{eab_str} [{p.get('cert_days')}d]")
    print("=" * 60)


def cmd_setup(args):
    """Flag-based setup command."""
    cfg = load_config()
    ca = args.ca.lower().strip()
    if ca not in cfg.get("providers", {}):
        print(f"[\033[91mERROR\033[0m] Unknown CA provider '{ca}'. Available: {list(cfg.get('providers', {}).keys())}")
        sys.exit(1)

    cfg["active_ca"] = ca
    pinfo = cfg["providers"][ca]

    if args.email:
        pinfo["email"] = args.email.strip()
        cfg["email"] = args.email.strip()

    if args.kid:
        pinfo["eab_kid"] = args.kid.strip()

    if args.hmac:
        pinfo["eab_hmac_key"] = args.hmac.strip()

    if args.api_key:
        pinfo["api_key"] = args.api_key.strip()

    if args.enable:
        cfg["enabled"] = True

    save_config(cfg)
    print(f"[\033[92mOK\033[0m] Provider '{pinfo.get('name')}' successfully configured.")
    if cfg.get("enabled"):
        print("[\033[92mOK\033[0m] aacert is now ENABLED.")
    else:
        print("[\033[93mINFO\033[0m] Module is currently DISABLED. Pass --enable or run: aacert enable")


def cmd_enable(args):
    cfg = load_config()
    cfg["enabled"] = True
    save_config(cfg)
    print("[\033[92mOK\033[0m] aacert ENABLED.")
    print(f"Active provider is: {cfg.get('active_ca')}")
    if not is_patch_installed():
        print("[\033[93mNOTE\033[0m] Hook patch not installed. Run: aacert install")


def cmd_disable(args):
    cfg = load_config()
    cfg["enabled"] = False
    save_config(cfg)
    print("[\033[92mOK\033[0m] aacert DISABLED.")
    print("aaPanel will now use native Let's Encrypt default.")


def cmd_set_ca(args):
    cfg = load_config()
    ca = args.ca_name.lower().strip()
    if ca not in cfg.get("providers", {}):
        print(f"[\033[91mERROR\033[0m] Unknown CA '{ca}'. Available: {list(cfg.get('providers', {}).keys())}")
        sys.exit(1)

    cfg["active_ca"] = ca
    save_config(cfg)
    pinfo = cfg["providers"][ca]
    print(f"[\033[92mOK\033[0m] Active CA changed to: \033[96m{pinfo.get('name')}\033[0m ({ca})")
    if pinfo.get("eab_required"):
        kid = pinfo.get("eab_kid", "").strip()
        hmac_k = pinfo.get("eab_hmac_key", "").strip()
        if not kid or not hmac_k:
            print("[\033[93mWARNING\033[0m] This provider requires EAB credentials. Set them with:")
            print(f"  aacert setup --ca {ca} --kid <KID> --hmac <HMAC>")


def cmd_set_eab(args):
    cfg = load_config()
    ca = args.ca_name.lower().strip()
    if ca not in cfg.get("providers", {}):
        print(f"[\033[91mERROR\033[0m] Provider '{ca}' not found.")
        sys.exit(1)

    cfg["providers"][ca]["eab_kid"] = args.kid.strip()
    cfg["providers"][ca]["eab_hmac_key"] = args.hmac.strip()
    if args.email:
        cfg["providers"][ca]["email"] = args.email.strip()
        cfg["email"] = args.email.strip()
    save_config(cfg)
    print(f"[\033[92mOK\033[0m] EAB credentials updated for provider '{ca}'.")


def cmd_test_conn(args):
    cfg = load_config()
    ca = (args.ca_name or cfg.get("active_ca", "letsencrypt")).lower().strip()
    if ca not in cfg.get("providers", {}):
        print(f"[\033[91mERROR\033[0m] Provider '{ca}' not found.")
        sys.exit(1)

    url = cfg["providers"][ca].get("directory_url")
    print(f"Testing connection to {cfg['providers'][ca].get('name')}...")
    print(f"URL: {url}")

    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": f"aacert/{VERSION}"})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            status = resp.getcode()
            body = json.loads(resp.read().decode("utf-8"))
            print(f"[\033[92mSUCCESS\033[0m] HTTP {status}")
            print(f"  newAccount : {body.get('newAccount')}")
            print(f"  newOrder   : {body.get('newOrder')}")
            print(f"  newNonce   : {body.get('newNonce')}")
    except Exception as e:
        print(f"[\033[91mFAILED\033[0m] {str(e)}")


def cmd_install(args):
    """Install hook patch into aaPanel."""
    import subprocess
    script = os.path.join(BASE_DIR, "install.sh")
    if not os.path.exists(script):
        print("[!] install.sh not found.")
        sys.exit(1)
    subprocess.run(["bash", script], check=True)


def cmd_uninstall(args):
    """Uninstall hook patch from aaPanel."""
    import subprocess
    script = os.path.join(BASE_DIR, "uninstall.sh")
    if not os.path.exists(script):
        print("[!] uninstall.sh not found.")
        sys.exit(1)
    subprocess.run(["bash", script], check=True)


def main():
    parser = argparse.ArgumentParser(
        prog="aacert",
        description="aacert - Multi-CA ACME Manager for aaPanel",
        epilog="https://github.com/dyzulk/aacert"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # version
    subparsers.add_parser("version", help="Show aacert version")

    # status
    subparsers.add_parser("status", help="Show current status and active CA")

    # setup
    p_setup = subparsers.add_parser("setup", help="Configure a CA provider with credentials")
    p_setup.add_argument("--ca", required=True, help="Provider (zerossl, google, ssl_com, letsencrypt)")
    p_setup.add_argument("--email", help="Account email address")
    p_setup.add_argument("--kid", help="EAB Key ID")
    p_setup.add_argument("--hmac", help="EAB HMAC Key")
    p_setup.add_argument("--api-key", help="Provider API Key (optional)")
    p_setup.add_argument("--enable", action="store_true", help="Enable module after setup")

    # enable / disable
    subparsers.add_parser("enable", help="Enable aacert (activate custom CA)")
    subparsers.add_parser("disable", help="Disable aacert (revert to Let's Encrypt)")

    # set-ca
    p_set_ca = subparsers.add_parser("set-ca", help="Switch active CA provider")
    p_set_ca.add_argument("ca_name", help="Provider name")

    # set-eab
    p_set_eab = subparsers.add_parser("set-eab", help="Set EAB credentials for a provider")
    p_set_eab.add_argument("ca_name", help="Provider name")
    p_set_eab.add_argument("--kid", required=True, help="EAB Key ID")
    p_set_eab.add_argument("--hmac", required=True, help="EAB HMAC Key")
    p_set_eab.add_argument("--email", help="Account email")

    # test
    p_test = subparsers.add_parser("test", help="Test connection to ACME directory")
    p_test.add_argument("ca_name", nargs="?", default=None, help="Provider to test")

    # install / uninstall
    subparsers.add_parser("install", help="Install hook patch into aaPanel")
    subparsers.add_parser("uninstall", help="Remove hook patch from aaPanel")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    dispatch = {
        "version": cmd_version,
        "status": cmd_status,
        "setup": cmd_setup,
        "enable": cmd_enable,
        "disable": cmd_disable,
        "set-ca": cmd_set_ca,
        "set-eab": cmd_set_eab,
        "test": cmd_test_conn,
        "install": cmd_install,
        "uninstall": cmd_uninstall,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()

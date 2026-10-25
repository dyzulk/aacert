# coding: utf-8
import argparse
from aacert_core import __version__


class AacertArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        import sys
        print(f"\n[\033[91mERROR\033[0m] {message}\n")
        print("Available commands:")
        print("  status       - Show active CA provider and status")
        print("  setup        - Configure CA credentials (ZeroSSL, Google, SSL.com)")
        print("  enable       - Activate custom CA provider")
        print("  disable      - Revert aaPanel to native Let's Encrypt")
        print("  set-ca       - Switch active CA provider")
        print("  set-eab      - Update EAB KID and HMAC credentials")
        print("  test         - Test ACME directory connectivity")
        print("  install      - Install aaPanel hook patch")
        print("  uninstall    - Remove hook patch from aaPanel")
        print("  version      - Show version information")
        print("  help         - Show complete help and usage examples\n")
        print("Run 'aacert help' or 'aacert <command> --help' for details.")
        sys.exit(2)


def build_parser() -> argparse.ArgumentParser:
    parser = AacertArgumentParser(
        prog="aacert",
        description="aacert - Multi-CA ACME Manager for aaPanel",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # version
    subparsers.add_parser("version", help="Show version information")

    # status
    subparsers.add_parser("status", help="Show active CA provider and status")

    # setup
    p_setup = subparsers.add_parser("setup", help="Configure provider credentials")
    p_setup.add_argument("--ca", required=True, help="Provider ID (zerossl, google, ssl_com, letsencrypt)")
    p_setup.add_argument("--email", help="Account registration email")
    p_setup.add_argument("--kid", help="EAB Key Identifier (KID)")
    p_setup.add_argument("--hmac", help="EAB HMAC Key")
    p_setup.add_argument("--api-key", help="ZeroSSL REST API Key (optional)")
    p_setup.add_argument("--enable", action="store_true", help="Enable aacert immediately")

    # enable
    subparsers.add_parser("enable", help="Enable aacert custom CA provider")

    # disable
    subparsers.add_parser("disable", help="Disable aacert (fallback to native Let's Encrypt)")

    # set-ca
    p_setca = subparsers.add_parser("set-ca", help="Switch active CA provider")
    p_setca.add_argument("ca_name", help="Provider ID (letsencrypt, zerossl, google, ssl_com)")

    # set-eab
    p_seteab = subparsers.add_parser("set-eab", help="Set EAB KID and HMAC key")
    p_seteab.add_argument("ca_name", help="Provider ID (zerossl, google)")
    p_seteab.add_argument("--kid", required=True, help="EAB Key ID")
    p_seteab.add_argument("--hmac", required=True, help="EAB HMAC Key")
    p_seteab.add_argument("--email", help="Account email")

    # test
    p_test = subparsers.add_parser("test", help="Test connectivity to ACME directory")
    p_test.add_argument("ca_name", nargs="?", help="Provider ID (default: active provider)")

    # install
    subparsers.add_parser("install", help="Install hook patch into aaPanel")

    # uninstall
    subparsers.add_parser("uninstall", help="Uninstall hook patch and revert aaPanel")

    # doctor
    p_doc = subparsers.add_parser("doctor", help="Audit aaPanel letsencrypt_v2.json state and integrity")
    p_doc.add_argument("--clean-pending", action="store_true", help="Purge stale pending orders")

    # help
    subparsers.add_parser("help", help="Show help and examples")

    return parser

# coding: utf-8
import sys
from aacert_core.cli.parser import build_parser
from aacert_core.cli import (
    handle_version,
    handle_status,
    handle_setup,
    handle_enable,
    handle_disable,
    handle_set_ca,
    handle_set_eab,
    handle_test,
    handle_install,
    handle_uninstall,
    handle_doctor,
)


def run_cli(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv or sys.argv[1:])

    if not args.command or args.command == "help":
        parser.print_help()
        return 0

    dispatch = {
        "version": handle_version,
        "status": handle_status,
        "setup": handle_setup,
        "enable": handle_enable,
        "disable": handle_disable,
        "set-ca": handle_set_ca,
        "set-eab": handle_set_eab,
        "test": handle_test,
        "install": handle_install,
        "uninstall": handle_uninstall,
        "doctor": handle_doctor,
    }

    handler = dispatch.get(args.command)
    if handler:
        handler(args)
        return 0
    else:
        parser.print_help()
        return 1

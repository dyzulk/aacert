# coding: utf-8
"""Command line interface package for aacert."""
from aacert_core.cli.parser import build_parser
from aacert_core.cli.commands import (
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

__all__ = [
    "build_parser",
    "handle_version",
    "handle_status",
    "handle_setup",
    "handle_enable",
    "handle_disable",
    "handle_set_ca",
    "handle_set_eab",
    "handle_test",
    "handle_install",
    "handle_uninstall",
    "handle_doctor",
]

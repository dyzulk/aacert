#!/usr/bin/env python3
# coding: utf-8
import os
import sys
import unittest

GREEN = "\033[92m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

TESTS_DIR = os.path.dirname(os.path.realpath(__file__))
REPO_ROOT = os.path.dirname(TESTS_DIR)

if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


def main():
    print("=" * 65)
    print(f"{BOLD}Running aacert Modular Test Suite{RESET}")
    print("=" * 65)

    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=TESTS_DIR, pattern="test_*.py", top_level_dir=REPO_ROOT)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("=" * 65)
    if result.wasSuccessful():
        print(f"{GREEN}{BOLD}✓ ALL TESTS PASSED ({result.testsRun} tests executed){RESET}")
        return 0
    else:
        print(f"{RED}{BOLD}✗ TESTS FAILED (Failures: {len(result.failures)}, Errors: {len(result.errors)}){RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

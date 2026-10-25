# coding: utf-8
# ====================================================================
# RFC 8555 External Account Binding (EAB) Helper Proxy
# https://github.com/dyzulk/aacert
# ====================================================================

import os
import sys

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from aacert_core.lib.eab import (
    build_eab_object,
    b64url_decode,
    extract_jwk_from_pem,
)
from aacert_core.lib.jws import b64url as b64url_encode

__all__ = ["build_eab_object", "b64url_encode", "b64url_decode", "extract_jwk_from_pem"]

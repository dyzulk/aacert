# coding: utf-8
import ssl
import json
import urllib.request
from typing import Dict, Any


class NetworkService:
    @staticmethod
    def test_directory(url: str, user_agent: str = "aacert/1.0.3") -> Dict[str, Any]:
        """Test HTTP connectivity and parse ACME directory JSON."""
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, headers={"User-Agent": user_agent})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            status = resp.getcode()
            body = json.loads(resp.read().decode("utf-8"))
            return {
                "status": status,
                "endpoints": {
                    "newAccount": body.get("newAccount"),
                    "newOrder": body.get("newOrder"),
                    "newNonce": body.get("newNonce"),
                    "revokeCert": body.get("revokeCert"),
                    "keyChange": body.get("keyChange"),
                }
            }

# coding: utf-8
from dataclasses import dataclass
from typing import Optional


@dataclass
class ProviderProfile:
    id: str
    name: str
    directory_url: str
    staging_url: str
    eab_required: bool = False
    cert_days: int = 90
    description: str = ""
    eab_kid: Optional[str] = None
    eab_hmac_key: Optional[str] = None
    email: Optional[str] = None
    maintenance: bool = False
    maintenance_message: str = ""

    def get_active_url(self, is_debug: bool = False) -> str:
        return self.staging_url if is_debug else self.directory_url

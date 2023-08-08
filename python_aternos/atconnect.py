"""Stores API session and sends requests"""

import string
import secrets

from typing import Optional
from typing import Dict, Any


BASE_URL = 'https://aternos.org'
AJAX_URL = f'{BASE_URL}/ajax'

SEC_ALPHABET = string.ascii_lowercase + string.digits


class AternosConnect:
    """Class for sending API requests,
    bypassing Cloudflare and parsing responses"""

    def __init__(self) -> None:

        self.sec = ''
        self.token = ''
        self.atcookie = ''

    def parse_token(self) -> str:
        return ''

    def generate_sec(self) -> str:
        return 'a:b'

    def generate_sec_part(self) -> str:
        """Generates a part for SEC token"""

        return ''.join(
            secrets.choice(SEC_ALPHABET)
            for _ in range(11)
        ) + ('0' * 5)

    def request_cloudflare(
            self, url: str, method: str,
            params: Optional[Dict[Any, Any]] = None,
            data: Optional[Dict[Any, Any]] = None,
            headers: Optional[Dict[Any, Any]] = None,
            reqcookies: Optional[Dict[Any, Any]] = None,
            sendtoken: bool = False,
            retries: int = 5,
            timeout: int = 4) -> Any:
        return None

    @property
    def atsession(self) -> str:
        """Aternos session cookie,
        empty string if not logged in

        Returns:
            Session cookie
        """

        return self.session.cookies.get(
            'ATERNOS_SESSION', ''
        )

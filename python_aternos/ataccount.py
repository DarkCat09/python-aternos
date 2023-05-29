"""Methods related to an Aternos account
including servers page parsing"""

import re
import base64

from typing import List, Dict
from typing import TYPE_CHECKING

import lxml.html

from .atlog import log
from .atmd5 import md5encode

from .atconnect import AternosConnect
from .atconnect import BASE_URL, AJAX_URL

from .atserver import AternosServer

if TYPE_CHECKING:
    from .atclient import Client


ACCOUNT_URL = f'{AJAX_URL}/account'
email_re = re.compile(
    r'^[A-Za-z0-9\-_+.]+@[A-Za-z0-9\-_+.]+\.[A-Za-z0-9\-]+$|^$'
)


class AternosAccount:
    """Methods related to an Aternos account
    including servers page parsing"""

    def __init__(self, atclient: 'Client') -> None:
        """Should not be instantiated manually,
        the entrypoint is `atclient.Client`

        Args:
            atconn (AternosConnect): AternosConnect object
        """

        self.atclient = atclient
        self.atconn: AternosConnect = atclient.atconn

        self.parsed = False
        self.servers: List[AternosServer] = []

    def list_servers(self, cache: bool = True) -> List[AternosServer]:
        """Parses a servers list

        Args:
            cache (bool, optional): If the function should use
                cached servers list (recommended)

        Returns:
            List of AternosServer objects
        """

        if cache and self.parsed:
            return self.servers

        serverspage = self.atconn.request_cloudflare(
            f'{BASE_URL}/servers/', 'GET'
        )
        serverstree = lxml.html.fromstring(serverspage.content)

        servers = serverstree.xpath(
            '//div[@class="server-body"]/@data-id'
        )
        self.refresh_servers(servers)

        # Update session file (add servers)
        try:
            self.atclient.save_session(self.atclient.saved_session)
        except OSError as err:
            log.warning('Unable to save servers list to file: %s', err)

        return self.servers

    def refresh_servers(self, ids: List[str]) -> None:
        """Replaces the cached servers list
        creating AternosServer objects by given IDs

        Args:
            ids (List[str]): Servers unique identifiers
        """

        self.servers = []
        for s in ids:

            servid = s.strip()
            if servid == '':
                continue

            log.debug('Adding server %s', servid)
            srv = AternosServer(servid, self.atconn)
            self.servers.append(srv)

        self.parsed = True

    def get_server(self, servid: str) -> AternosServer:
        """Creates a server object from the server ID.
        Use this instead of `list_servers` if you know
        the server IDentifier

        Returns:
            AternosServer object
        """

        return AternosServer(servid, self.atconn)

    def change_username(self, value: str) -> None:
        """Changes a username in your Aternos account

        Args:
            value (str): New username
        """

        self.atconn.request_cloudflare(
            f'{ACCOUNT_URL}/username',
            'POST', data={'username': value},
            sendtoken=True,
        )

    def change_email(self, value: str) -> None:
        """Changes an e-mail in your Aternos account

        Args:
            value (str): New e-mail

        Raises:
            ValueError: If an invalid e-mail address
                was passed to the function
        """

        if not email_re.match(value):
            raise ValueError('Invalid e-mail')

        self.atconn.request_cloudflare(
            f'{ACCOUNT_URL}/email',
            'POST', data={'email': value},
            sendtoken=True,
        )

    def change_password(self, old: str, new: str) -> None:
        """Changes a password in your Aternos account

        Args:
            old (str): Old password
            new (str): New password
        """

        self.change_password_hashed(
            md5encode(old),
            md5encode(new),
        )

    def change_password_hashed(self, old: str, new: str) -> None:
        """Changes a password in your Aternos account.
        Unlike `change_password`, this function
        takes hashed passwords as the arguments

        Args:
            old (str): Old password hashed with MD5
            new (str): New password hashed with MD5
        """

        self.atconn.request_cloudflare(
            f'{ACCOUNT_URL}/password',
            'POST', data={
                'oldpassword': old,
                'newpassword': new,
            },
            sendtoken=True,
        )

    def qrcode_2fa(self) -> Dict[str, str]:
        """Requests a secret code and
        a QR code for enabling 2FA"""

        return self.atconn.request_cloudflare(
            f'{ACCOUNT_URL}/secret',
            'GET', sendtoken=True,
        ).json()

    def save_qr(self, qrcode: str, filename: str) -> None:
        """Writes a 2FA QR code into a png-file

        Args:
            qrcode (str): Base64 encoded png image from `qrcode_2fa()`
            filename (str): Where the QR code image must be saved.
                Existing file will be rewritten.
        """

        data = qrcode.removeprefix('data:image/png;base64,')
        png = base64.b64decode(data)

        with open(filename, 'wb') as f:
            f.write(png)

    def enable_2fa(self, code: int) -> None:
        """Enables Two-Factor Authentication

        Args:
            code (int): 2FA code
        """

        self.atconn.request_cloudflare(
            f'{ACCOUNT_URL}/twofactor',
            'POST', data={'code': code},
            sendtoken=True,
        )

    def disable_2fa(self, code: int) -> None:
        """Disables Two-Factor Authentication

        Args:
            code (int): 2FA code
        """

        self.atconn.request_cloudflare(
            f'{ACCOUNT_URL}/disbaleTwofactor',
            'POST', data={'code': code},
            sendtoken=True,
        )

    def logout(self) -> None:
        """The same as `atclient.Client.logout`"""

        self.atclient.logout()

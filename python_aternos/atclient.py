"""Entry point. Authorizes on Aternos
and allows to manage your account"""

import os
import re
import hashlib
import lxml.html
from typing import List, Optional

from .atserver import AternosServer
from .atconnect import AternosConnect
from .aterrors import CredentialsError


class Client:

    """Aternos API Client class object of which contains user's auth data

    :param atconn: :class:`python_aternos.atconnect.AternosConnect`
    instance with initialized Aternos session
    :type atconn: python_aternos.atconnect.AternosConnect
    """

    def __init__(
            self,
            atconn: AternosConnect,
            servers: Optional[List[str]] = None) -> None:

        self.atconn = atconn
        self.parsed = False
        self.servers: List[AternosServer] = []

        if servers:
            self.refresh_servers(servers)

    @classmethod
    def from_hashed(cls, username: str, md5: str):

        """Log in to Aternos with a username and a hashed password

        :param username: Your username
        :type username: str
        :param md5: Your password hashed with MD5
        :type md5: str
        :raises CredentialsError: If the API
        doesn't return a valid session cookie
        :return: Client instance
        :rtype: python_aternos.Client
        """

        atconn = AternosConnect()
        atconn.parse_token()
        atconn.generate_sec()

        credentials = {
            'user': username,
            'password': md5
        }

        loginreq = atconn.request_cloudflare(
            'https://aternos.org/panel/ajax/account/login.php',
            'POST', data=credentials, sendtoken=True
        )

        if 'ATERNOS_SESSION' not in loginreq.cookies:
            raise CredentialsError(
                'Check your username and password'
            )

        return cls(atconn)

    @classmethod
    def from_credentials(cls, username: str, password: str):

        """Log in to Aternos with a username and a plain password

        :param username: Your username
        :type username: str
        :param password: Your password without any encryption
        :type password: str
        :return: Client instance
        :rtype: python_aternos.Client
        """

        md5 = Client.md5encode(password)
        return cls.from_hashed(username, md5)

    @classmethod
    def from_session(
            cls,
            session: str,
            servers: Optional[List[str]] = None):

        """Log in to Aternos using a session cookie value

        :param session: Value of ATERNOS_SESSION cookie
        :type session: str
        :return: Client instance
        :rtype: python_aternos.Client
        """

        atconn = AternosConnect()
        atconn.session.cookies['ATERNOS_SESSION'] = session
        atconn.parse_token()
        atconn.generate_sec()

        return cls(atconn, servers)

    @classmethod
    def restore_session(cls, file: str = '~/.aternos'):

        """Log in to Aternos using a saved ATERNOS_SESSION cookie

        :param file: File where a session cookie
        was saved, deafults to `~/.aternos`
        :type file: str, optional
        :return: Client instance
        :rtype: python_aternos.Client
        """

        file = os.path.expanduser(file)
        with open(file, 'rt') as f:
            saved = f.read().replace('\r\n', '\n').split('\n')

        session = saved[0].strip()

        if len(saved) > 1:
            return cls.from_session(
                session=session,
                servers=saved[1:]
            )

        return cls.from_session(session)

    @staticmethod
    def md5encode(passwd: str) -> str:

        """Encodes the given string with MD5

        :param passwd: String to encode
        :type passwd: str
        :return: Hexdigest hash of the string in lowercase
        :rtype: str
        """

        encoded = hashlib.md5(passwd.encode('utf-8'))
        return encoded.hexdigest().lower()

    def save_session(
            self,
            file: str = '~/.aternos',
            incl_servers: bool = True) -> None:

        """Saves an ATERNOS_SESSION cookie to a file

        :param file: File where a session cookie
        must be saved, defaults to `~/.aternos`
        :type file: str, optional
        :param incl_servers: If the function
        should include the servers IDs to
        reduce API requests count (recommended),
        defaults to True
        :type incl_servers: bool, optional
        """

        file = os.path.expanduser(file)
        with open(file, 'wt') as f:

            f.write(self.atconn.atsession + '\n')
            if not incl_servers:
                return

            for s in self.servers:
                f.write(s.servid + '\n')

    def list_servers(self, cache: bool = True) -> List[AternosServer]:

        """Parses a list of your servers from Aternos website

        :param cache: If the function should use
        cached servers list (recommended), defaults to True
        :type cache: bool, optional
        :return: List of :class:`python_aternos.atserver.AternosServer` objects
        :rtype: list
        """

        if cache and self.parsed:
            return self.servers

        serverspage = self.atconn.request_cloudflare(
            'https://aternos.org/servers/', 'GET'
        )
        serverstree = lxml.html.fromstring(serverspage.content)

        servers = serverstree.xpath(
            '/html/body/div[1]/main/div[3]/section/div[1]/div[2]/div'
            '/div[@class="server-body"]/@data-id'
        )
        self.refresh_servers(servers)

        return self.servers

    def refresh_servers(self, ids: List[str]) -> None:

        """Replaces cached servers list creating
        :class:`AternosServer` objects by given IDs

        :param ids: Servers unique identifiers
        :type ids: List[str]
        """

        self.servers = []
        for s in ids:

            servid = s.strip()
            if servid == '':
                continue

            srv = AternosServer(servid, self.atconn)
            self.servers.append(srv)

        self.parsed = True

    def get_server(self, servid: str) -> AternosServer:

        """Creates a server object from the server ID.
        Use this instead of list_servers if you know the ID to save some time.

        :return: :class:`python_aternos.atserver.AternosServer` object
        :rtype: python_aternos.atserver.AternosServer
        """

        return AternosServer(servid, self.atconn)

    def change_username(self, value: str) -> None:

        """Changes a username in your Aternos account

        :param value: New username
        :type value: str
        """

        self.atconn.request_cloudflare(
            'https://aternos.org/panel/ajax/account/username.php',
            'POST', data={'username': value}
        )

    def change_email(self, value: str) -> None:

        """Changes an e-mail in your Aternos account

        :param value: New e-mail
        :type value: str
        :raises ValueError: If an invalid
        e-mail address was passed to the function
        """

        email = re.compile(
            r'^[A-Za-z0-9\-_+.]+@[A-Za-z0-9\-_+.]+\.[A-Za-z0-9\-]+$|^$'
        )
        if not email.match(value):
            raise ValueError('Invalid e-mail!')

        self.atconn.request_cloudflare(
            'https://aternos.org/panel/ajax/account/email.php',
            'POST', data={'email': value}
        )

    def change_password(self, old: str, new: str) -> None:

        """Changes a password in your Aternos account

        :param old: Old password
        :type old: str
        :param new: New password
        :type new: str
        """

        old = Client.md5encode(old)
        new = Client.md5encode(new)
        self.atconn.request_cloudflare(
            'https://aternos.org/panel/ajax/account/password.php',
            'POST', data={
                'oldpassword': old,
                'newpassword': new
            }
        )

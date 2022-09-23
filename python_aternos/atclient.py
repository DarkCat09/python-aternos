"""Entry point. Authorizes on Aternos
and allows to manage your account"""

import os
import re
import hashlib
import logging

from typing import List, Optional

import lxml.html

from .atserver import AternosServer
from .atconnect import AternosConnect
from .aterrors import CredentialsError


class Client:

    """Aternos API Client class, object
    of which contains user's auth data"""

    def __init__(
            self,
            atconn: AternosConnect,
            servers: Optional[List[str]] = None) -> None:

        """Aternos API Client class, object
        of which contains user's auth data

        Args:
            atconn (AternosConnect):
                AternosConnect instance with initialized Aternos session
            servers (Optional[List[str]], optional):
                List with servers IDs
        """

        self.atconn = atconn
        self.parsed = False
        self.servers: List[AternosServer] = []

        if servers:
            self.refresh_servers(servers)

    @classmethod
    def from_hashed(
            cls,
            username: str,
            md5: str,
            sessions_dir: str = '~'):

        """Log in to an Aternos account with
        a username and a hashed password

        Args:
            username (str): Your username
            md5 (str): Your password hashed with MD5
            sessions_dir (str): Path to the directory
                where session will be automatically saved

        Raises:
            CredentialsError: If the API didn't
                return a valid session cookie
        """

        atconn = AternosConnect()
        atconn.parse_token()
        atconn.generate_sec()

        secure = cls.secure_name(username)
        filename = f'{sessions_dir}/.at_{secure}'

        try:
            return cls.restore_session(filename)
        except (OSError, CredentialsError):
            pass

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

        obj = cls(atconn)

        try:
            obj.save_session(filename)
        except OSError:
            pass

        return obj

    @classmethod
    def from_credentials(
            cls,
            username: str,
            password: str,
            sessions_dir: str = '~'):

        """Log in to Aternos with a username and a plain password

        Args:
            username (str): Your username
            password (str): Your password without any encryption
            sessions_dir (str): Path to the directory
                where session will be automatically saved
        """

        md5 = Client.md5encode(password)
        return cls.from_hashed(
            username, md5,
            sessions_dir
        )

    @classmethod
    def from_session(
            cls,
            session: str,
            servers: Optional[List[str]] = None):

        """Log in to Aternos using a session cookie value

        Args:
            session (str): Value of ATERNOS_SESSION cookie
        """

        atconn = AternosConnect()
        atconn.session.cookies['ATERNOS_SESSION'] = session
        atconn.parse_token()
        atconn.generate_sec()

        return cls(atconn, servers)

    @classmethod
    def restore_session(cls, file: str = '~/.aternos'):

        """Log in to Aternos using a saved ATERNOS_SESSION cookie

        Args:
            file (str, optional): File where a session cookie was saved
        """

        file = os.path.expanduser(file)
        logging.debug(f'Restoring session from {file}')

        if not os.path.exists(file):
            raise FileNotFoundError()

        with open(file, 'rt', encoding='utf-8') as f:
            saved = f.read() \
                .strip() \
                .replace('\r\n', '\n') \
                .split('\n')

        session = saved[0].strip()
        if session == '':
            raise CredentialsError(
                'Unable to read session cookie, '
                'the first line is empty'
            )

        if len(saved) > 1:
            return cls.from_session(
                session=session,
                servers=saved[1:]
            )

        return cls.from_session(session)

    @staticmethod
    def md5encode(passwd: str) -> str:

        """Encodes the given string with MD5

        Args:
            passwd (str): String to encode

        Returns:
            Hexdigest hash of the string in lowercase
        """

        encoded = hashlib.md5(passwd.encode('utf-8'))
        return encoded.hexdigest().lower()

    @staticmethod
    def secure_name(filename: str, repl: str = '_') -> str:

        """Replaces unsecure characters
        in filename to underscore or `repl`

        Args:
            filename (str): Filename
            repl (str, optional): Replacement
                for unsafe characters

        Returns:
            str: Secure filename
        """

        return re.sub(
            r'[^A-Za-z0-9_-]',
            repl, filename
        )

    def save_session(
            self,
            file: str = '~/.aternos',
            incl_servers: bool = True) -> None:

        """Saves an ATERNOS_SESSION cookie to a file

        Args:
            file (str, optional): File where a session cookie must be saved
            incl_servers (bool, optional): If the function
                should include the servers IDs to
                reduce API requests count (recommended)
        """

        file = os.path.expanduser(file)
        logging.debug(f'Saving session to {file}')

        with open(file, 'wt', encoding='utf-8') as f:

            f.write(self.atconn.atsession + '\n')
            if not incl_servers:
                return

            for s in self.servers:
                f.write(s.servid + '\n')

    def list_servers(self, cache: bool = True) -> List[AternosServer]:

        """Parses a list of your servers from Aternos website

        Args:
            cache (bool, optional): If the function should use
                cached servers list (recommended)

        Returns:
            List of AternosServer objects
        """

        if cache and self.parsed:
            return self.servers

        serverspage = self.atconn.request_cloudflare(
            'https://aternos.org/servers/', 'GET'
        )
        serverstree = lxml.html.fromstring(serverspage.content)

        servers = serverstree.xpath(
            '//div[@class="server-body"]/@data-id'
        )
        self.refresh_servers(servers)

        return self.servers

    def refresh_servers(self, ids: List[str]) -> None:

        """Replaces cached servers list creating
        AternosServer objects by given IDs

        Args:
            ids (List[str]): Servers unique identifiers
        """

        self.servers = []
        for s in ids:

            servid = s.strip()
            if servid == '':
                continue

            logging.debug(f'Adding server {servid}')
            srv = AternosServer(servid, self.atconn)
            self.servers.append(srv)

        self.parsed = True

    def get_server(self, servid: str) -> AternosServer:

        """Creates a server object from the server ID.
        Use this instead of list_servers
        if you know the ID to save some time.

        Returns:
            AternosServer object
        """

        return AternosServer(servid, self.atconn)

    def logout(self) -> None:

        """Log out from Aternos account"""

        self.atconn.request_cloudflare(
            'https://aternos.org/panel/ajax/account/logout.php',
            'GET', sendtoken=True
        )

    def change_username(self, value: str) -> None:

        """Changes a username in your Aternos account

        Args:
            value (str): New username
        """

        self.atconn.request_cloudflare(
            'https://aternos.org/panel/ajax/account/username.php',
            'POST', data={'username': value}, sendtoken=True
        )

    def change_email(self, value: str) -> None:

        """Changes an e-mail in your Aternos account

        Args:
            value (str): New e-mail

        Raises:
            ValueError: If an invalid e-mail address
                was passed to the function
        """

        email = re.compile(
            r'^[A-Za-z0-9\-_+.]+@[A-Za-z0-9\-_+.]+\.[A-Za-z0-9\-]+$|^$'
        )
        if not email.match(value):
            raise ValueError('Invalid e-mail!')

        self.atconn.request_cloudflare(
            'https://aternos.org/panel/ajax/account/email.php',
            'POST', data={'email': value}, sendtoken=True
        )

    def change_password(self, old: str, new: str) -> None:

        """Changes a password in your Aternos account

        Args:
            old (str): Old password
            new (str): New password
        """

        self.change_password_hashed(
            Client.md5encode(old),
            Client.md5encode(new),
        )

    def change_password_hashed(self, old: str, new: str) -> None:

        """Changes a password in your Aternos account.
        Unlike `change_password`, this function
        takes hashed passwords as arguments

        Args:
            old (str): Old password hashed with MD5
            new (str): New password hashed with MD5
        """

        self.atconn.request_cloudflare(
            'https://aternos.org/panel/ajax/account/password.php',
            'POST', data={
                'oldpassword': old,
                'newpassword': new
            }, sendtoken=True
        )

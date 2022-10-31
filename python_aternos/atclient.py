"""Entry point. Authorizes on Aternos
and allows to manage your account"""

import os
import re
import hashlib
import logging

import base64

from typing import List, Dict, Optional

import lxml.html

from .atserver import AternosServer
from .atconnect import AternosConnect
from .aterrors import CredentialsError
from .aterrors import TwoFactorAuthError


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

        self.saved_session = ''

        self.parsed = False
        self.servers: List[AternosServer] = []

        if servers:
            self.refresh_servers(servers)

    @classmethod
    def from_hashed(
            cls,
            username: str,
            md5: str,
            code: Optional[int] = None,
            sessions_dir: str = '~',
            **custom_args):
        """Log in to an Aternos account with
        a username and a hashed password

        Args:
            username (str): Your username
            md5 (str): Your password hashed with MD5
            code (Optional[int]): 2FA code
            sessions_dir (str): Path to the directory
                where session will be automatically saved
            **custom_args (tuple, optional): Keyword arguments
                which will be passed to CloudScraper `__init__`

        Raises:
            CredentialsError: If the API didn't
                return a valid session cookie
        """

        filename = cls.session_file(
            username, sessions_dir
        )

        try:
            return cls.restore_session(
                filename, **custom_args
            )
        except (OSError, CredentialsError):
            pass

        atconn = AternosConnect()

        if len(custom_args) > 0:
            atconn.add_args(**custom_args)

        atconn.parse_token()
        atconn.generate_sec()

        credentials = {
            'user': username,
            'password': md5,
        }

        if code is not None:
            credentials['code'] = str(code)

        loginreq = atconn.request_cloudflare(
            'https://aternos.org/panel/ajax/account/login.php',
            'POST', data=credentials, sendtoken=True
        )

        if b'"show2FA":true' in loginreq.content:
            raise TwoFactorAuthError('2FA code is required')

        if 'ATERNOS_SESSION' not in loginreq.cookies:
            raise CredentialsError(
                'Check your username and password'
            )

        obj = cls(atconn)
        obj.saved_session = filename

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
            code: Optional[int] = None,
            sessions_dir: str = '~',
            **custom_args):
        """Log in to Aternos with a username and a plain password

        Args:
            username (str): Your username
            password (str): Your password without any encryption
            code (Optional[int]): 2FA code
            sessions_dir (str): Path to the directory
                where session will be automatically saved
            **custom_args (tuple, optional): Keyword arguments
                which will be passed to CloudScraper `__init__`
        """

        md5 = Client.md5encode(password)
        return cls.from_hashed(
            username, md5, code,
            sessions_dir, **custom_args
        )

    @classmethod
    def from_session(
            cls,
            session: str,
            servers: Optional[List[str]] = None,
            **custom_args):
        """Log in to Aternos using a session cookie value

        Args:
            session (str): Value of ATERNOS_SESSION cookie
            **custom_args (tuple, optional): Keyword arguments
                which will be passed to CloudScraper `__init__`
        """

        atconn = AternosConnect()

        atconn.add_args(**custom_args)
        atconn.session.cookies['ATERNOS_SESSION'] = session

        atconn.parse_token()
        atconn.generate_sec()

        return cls(atconn, servers)

    @classmethod
    def restore_session(
            cls,
            file: str = '~/.aternos',
            **custom_args):
        """Log in to Aternos using
        a saved ATERNOS_SESSION cookie

        Args:
            file (str, optional): File where a session cookie was saved
            **custom_args (tuple, optional): Keyword arguments
                which will be passed to CloudScraper `__init__`
        """

        file = os.path.expanduser(file)
        logging.debug('Restoring session from %s', file)

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
            obj = cls.from_session(
                session=session,
                servers=saved[1:],
                **custom_args
            )
        else:
            obj = cls.from_session(
                session,
                **custom_args
            )

        obj.saved_session = file

        return obj

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
    def session_file(username: str, sessions_dir: str = '~') -> str:
        """Generates session file name
        for authenticated user

        Args:
            username (str): Authenticated user
            sessions_dir (str, optional): Path to directory
                with automatically saved sessions

        Returns:
            Filename
        """

        # unsafe symbols replacement
        repl = '_'

        secure = re.sub(
            r'[^A-Za-z0-9_-]',
            repl, username
        )

        return f'{sessions_dir}/.at_{secure}'

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
        logging.debug('Saving session to %s', file)

        with open(file, 'wt', encoding='utf-8') as f:

            f.write(self.atconn.atsession + '\n')
            if not incl_servers:
                return

            for s in self.servers:
                f.write(s.servid + '\n')

    def remove_session(self, file: str = '~/.aternos') -> None:
        """Removes a file which contains
        ATERNOS_SESSION cookie saved
        with `save_session()`

        Args:
            file (str, optional): Filename
        """

        file = os.path.expanduser(file)
        logging.debug('Removing session file: %s', file)

        try:
            os.remove(file)
        except OSError as err:
            logging.warning('Unable to delete session file: %s', err)

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

        # Update session file (add servers)
        try:
            self.save_session(self.saved_session)
        except OSError as err:
            logging.warning('Unable to save servers list to file: %s', err)

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

            logging.debug('Adding server %s', servid)
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

        self.remove_session(self.saved_session)

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
                'newpassword': new,
            }, sendtoken=True
        )

    def qrcode_2fa(self) -> Dict[str, str]:
        """Requests a secret code and
        a QR code for enabling 2FA"""

        return self.atconn.request_cloudflare(
            'https://aternos.org/panel/ajax/account/secret.php',
            'GET', sendtoken=True
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
            'https://aternos.org/panel/ajax/account/twofactor.php',
            'POST', data={
                'code': code
            }, sendtoken=True
        )

    def disable_2fa(self, code: int) -> None:
        """Disables Two-Factor Authentication

        Args:
            code (int): 2FA code
        """

        self.atconn.request_cloudflare(
            'https://aternos.org/panel/ajax/account/disbaleTwofactor.php',
            'POST', data={
                'code': code
            }, sendtoken=True
        )

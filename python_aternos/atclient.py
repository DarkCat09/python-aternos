"""Entry point. Authorizes on Aternos
and allows to manage your account"""

import os
import re
from typing import Optional, Type

from .atlog import log, is_debug, set_debug
from .atmd5 import md5encode

from .ataccount import AternosAccount

from .atconnect import AternosConnect
from .atconnect import AJAX_URL

from .aterrors import CredentialsError
from .aterrors import TwoFactorAuthError

from . import atjsparse
from .atjsparse import Interpreter
from .atjsparse import Js2PyInterpreter


class Client:
    """Aternos API Client class, object
    of which contains user's auth data"""

    def __init__(self) -> None:

        # Config
        self.sessions_dir = '~'
        self.js: Type[Interpreter] = Js2PyInterpreter
        # ###

        self.saved_session = '~/.aternos'  # will be rewritten by login()
        self.atconn = AternosConnect()
        self.account = AternosAccount(self)

    def login(
            self,
            username: str,
            password: str,
            code: Optional[int] = None) -> None:
        """Log in to your Aternos account
        with a username and a plain password

        Args:
            username (str): Username
            password (str): Plain-text password
            code (Optional[int], optional): 2FA code
        """

        self.login_hashed(
            username,
            md5encode(password),
            code,
        )

    def login_hashed(
            self,
            username: str,
            md5: str,
            code: Optional[int] = None) -> None:
        """Log in to your Aternos account
        with a username and a hashed password

        Args:
            username (str): Username
            md5 (str): Password hashed with MD5
            code (int): 2FA code

        Raises:
            TwoFactorAuthError: If the 2FA is enabled,
                but `code` argument was not passed or is incorrect
            CredentialsError: If the Aternos backend
                returned empty session cookie
                (usually because of incorrect credentials)
            ValueError: _description_
        """

        filename = self.session_filename(
            username, self.sessions_dir
        )

        try:
            self.restore_session(filename)
        except (OSError, CredentialsError):
            pass

        atjsparse.get_interpreter(create=self.js)
        self.atconn.parse_token()
        self.atconn.generate_sec()

        credentials = {
            'user': username,
            'password': md5,
        }

        if code is not None:
            credentials['code'] = str(code)

        loginreq = self.atconn.request_cloudflare(
            f'{AJAX_URL}/account/login',
            'POST', data=credentials, sendtoken=True,
        )

        if b'"show2FA":true' in loginreq.content:
            raise TwoFactorAuthError('2FA code is required')

        if 'ATERNOS_SESSION' not in loginreq.cookies:
            raise CredentialsError(
                'Check your username and password'
            )

        self.saved_session = filename
        try:
            self.save_session(filename)
        except OSError:
            pass

    def login_with_session(self, session: str) -> None:
        """Log in using ATERNOS_SESSION cookie

        Args:
            session (str): Session cookie value
        """

        self.atconn.parse_token()
        self.atconn.generate_sec()
        self.atconn.session.cookies['ATERNOS_SESSION'] = session

    def logout(self) -> None:
        """Log out from the Aternos account"""

        self.atconn.request_cloudflare(
            f'{AJAX_URL}/account/logout',
            'GET', sendtoken=True,
        )

        self.remove_session(self.saved_session)

    def restore_session(self, file: str = '~/.aternos') -> None:
        """Restores ATERNOS_SESSION cookie and,
        if included, servers list, from a session file

        Args:
            file (str, optional): Filename

        Raises:
            FileNotFoundError: If the file cannot be found
            CredentialsError: If the session cookie
                (or the file at all) has incorrect format
        """

        file = os.path.expanduser(file)
        log.debug('Restoring session from %s', file)

        if not os.path.exists(file):
            raise FileNotFoundError()

        with open(file, 'rt', encoding='utf-8') as f:
            saved = f.read() \
                .strip() \
                .replace('\r\n', '\n') \
                .split('\n')

        session = saved[0].strip()
        if session == '' or not session.isalnum():
            raise CredentialsError(
                'Session cookie is invalid or the file is empty'
            )

        if len(saved) > 1:
            self.account.refresh_servers(saved[1:])

        self.atconn.session.cookies['ATERNOS_SESSION'] = session
        self.saved_session = file

    def save_session(
            self,
            file: str = '~/.aternos',
            incl_servers: bool = True) -> None:
        """Saves an ATERNOS_SESSION cookie to a file

        Args:
            file (str, optional): File where a session cookie must be saved
            incl_servers (bool, optional): If the function
                should include the servers IDs in this file
                to reduce API requests count on the next restoration
                (recommended)
        """

        file = os.path.expanduser(file)
        log.debug('Saving session to %s', file)

        with open(file, 'wt', encoding='utf-8') as f:

            f.write(self.atconn.atsession + '\n')
            if not incl_servers:
                return

            for s in self.account.servers:
                f.write(s.servid + '\n')

    def remove_session(self, file: str = '~/.aternos') -> None:
        """Removes a file which contains
        ATERNOS_SESSION cookie saved
        with `save_session()`

        Args:
            file (str, optional): Filename
        """

        file = os.path.expanduser(file)
        log.debug('Removing session file: %s', file)

        try:
            os.remove(file)
        except OSError as err:
            log.warning('Unable to delete session file: %s', err)

    @staticmethod
    def session_filename(username: str, sessions_dir: str = '~') -> str:
        """Generates a session file name

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
            repl, username,
        )

        return f'{sessions_dir}/.at_{secure}'

    @property
    def debug(self) -> bool:
        return is_debug()

    @debug.setter
    def debug(self, state: bool) -> None:
        return set_debug(state)

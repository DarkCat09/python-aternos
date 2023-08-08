"""Entry point. Authorizes on Aternos
and allows to manage your account"""

import os
import re
from typing import Optional

from .atselenium import SeleniumHelper, Remote
from .atconnect import AJAX_URL

from .atlog import log, is_debug, set_debug
from .aterrors import CredentialsError


class Client:
    """Aternos API Client class, object
    of which contains user's auth data"""

    def __init__(self, driver: Remote) -> None:

        self.se = SeleniumHelper(driver)

        # Config
        self.sessions_dir = '~'
        # ###

        self.saved_session = '~/.aternos'  # will be rewritten by login()
        # self.atconn = AternosConnect()
        # self.account = AternosAccount(self)

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

        self.se.load_page('/go')

        user_input = self.se.find_by_id('user')
        user_input.clear()
        user_input.send_keys(username)

        pswd_input = self.se.find_by_id('password')
        pswd_input.clear()
        pswd_input.send_keys(password)

        err_msg = self.se.find_by_class('login-error')
        totp_input = self.se.find_by_id('twofactor-code')

        def logged_in_or_error(driver: Remote):
            return \
                driver.current_url.find('/servers') != -1 or \
                err_msg.is_displayed() or \
                totp_input.is_displayed()

        self.se.exec_js('login()')
        self.se.wait.until(logged_in_or_error)

        print(self.se.driver.get_cookie('ATERNOS_SESSION'))

    def login_with_session(self, session: str) -> None:
        """Log in using ATERNOS_SESSION cookie

        Args:
            session (str): Session cookie value
        """

        self.se.driver.add_cookie({
            'name': 'ATERNOS_SESSION',
            'value': session,
        })

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

"""Entry point. Authorizes on Aternos
and allows to manage your account"""

import os
import re
from typing import Optional, List

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement

from python_aternos.atserver import PartialServerInfo

from .atselenium import SeleniumHelper, Remote

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

        err_block = self.se.find_element(By.CLASS_NAME, 'login-error')
        err_alert = self.se.find_element(By.CLASS_NAME, 'alert-wrapper')

        self.se.exec_js(f'''
            document.getElementById('user').value = '{username}'
            document.getElementById('password').value = '{password}'
            document.getElementById('twofactor-code').value = '{code}'
            login()
        ''')

        def logged_in_or_error(driver: Remote):
            return (
                driver.current_url.find('/servers') != -1 or
                err_block.is_displayed() or
                err_alert.is_displayed()
            )

        self.se.wait.until(logged_in_or_error)

        if self.se.driver.current_url.find('/go') != -1:

            if err_block.is_displayed():
                raise CredentialsError(err_block.text)
            
            if err_alert.is_displayed():
                raise CredentialsError(err_alert.text)
        
        self.se.wait.until(lambda d: d.title.find('Cloudflare') == -1)

        if not self.se.get_cookie('ATERNOS_SESSION'):
            raise CredentialsError('Session cookie is empty')
        
        print(self.se.get_cookie('ATERNOS_SESSION'))  # TODO: remove, this is for debug

    def login_with_session(self, session: str) -> None:
        """Log in using ATERNOS_SESSION cookie

        Args:
            session (str): Session cookie value
        """

        self.se.set_cookie('ATERNOS_SESSION', session)

    def logout(self) -> None:
        """Log out from the Aternos account"""

        self.se.load_page('/servers')
        self.se.find_element(By.CLASS_NAME, 'logout').click()

        self.remove_session(self.saved_session)
    
    def list_servers(self) -> List[PartialServerInfo]:

        CARD_CLASS = 'servercard'
        
        self.se.load_page('/servers')

        def create_obj(s: WebElement) -> PartialServerInfo:
            return PartialServerInfo(
                id=s.get_dom_attribute('data-id'),
                name=s.get_dom_attribute('title'),
                software='',
                status=(
                    s
                    .get_dom_attribute('class')
                    .replace(CARD_CLASS, '')
                    .split()[0]
                ),
                players=0,
                se=self.se,
            )

        return list(map(
            create_obj,
            self.se.find_elements(By.CLASS_NAME, CARD_CLASS),
        ))

    def restore_session(self, file: str = '~/.aternos') -> None:
        """Restores ATERNOS_SESSION cookie from a session file

        Args:
            file (str, optional): Filename

        Raises:
            FileNotFoundError: If the file cannot be found
        """

        file = os.path.expanduser(file)
        log.debug('Restoring session from %s', file)

        if not os.path.exists(file):
            raise FileNotFoundError()

        with open(file, 'rt', encoding='utf-8') as f:
            session = f.readline().strip()

        self.login_with_session(session)
        self.saved_session = file

    def save_session(self, file: str = '~/.aternos') -> None:
        """Saves an ATERNOS_SESSION cookie to a file

        Args:
            file (str, optional):
                File where the session cookie must be saved
        """

        file = os.path.expanduser(file)
        log.debug('Saving session to %s', file)

        with open(file, 'wt', encoding='utf-8') as f:
            f.write(self.se.get_cookie('ATERNOS_SESSION') + '\n')

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

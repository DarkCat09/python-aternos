"""Stores API session and sends requests"""

import re
import time

import string
import secrets

from functools import partial

from typing import Optional
from typing import List, Dict, Any

import requests

from cloudscraper import CloudScraper

from .atlog import log, is_debug

from . import atjsparse
from .aterrors import TokenError
from .aterrors import CloudflareError
from .aterrors import AternosPermissionError


BASE_URL = 'https://aternos.org'
AJAX_URL = f'{BASE_URL}/ajax'

REQUA = \
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ' \
    '(KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36 OPR/85.0.4341.47'

ARROW_FN_REGEX = r'\(\(\).*?\)\(\);'
SCRIPT_TAG_REGEX = (
    rb'<script type=([\'"]?)text/javascript\1>.+?</script>'
)

SEC_ALPHABET = string.ascii_lowercase + string.digits


class AternosConnect:
    """Class for sending API requests,
    bypassing Cloudflare and parsing responses"""

    def __init__(self) -> None:

        self.session = CloudScraper()
        self.sec = ''
        self.token = ''
        self.atcookie = ''

    def refresh_session(self) -> None:
        """Creates a new CloudScraper
        session object and copies all cookies.
        Required for bypassing Cloudflare"""

        old_cookies = self.session.cookies
        captcha_kwarg = self.session.captcha
        self.session = CloudScraper(captcha=captcha_kwarg)
        self.session.cookies.update(old_cookies)
        del old_cookies

    def parse_token(self) -> str:
        """Parses Aternos ajax token that
        is needed for most requests

        Raises:
            TokenError: If the parser is unable
                to extract ajax token from HTML

        Returns:
            Aternos ajax token
        """

        loginpage = self.request_cloudflare(
            f'{BASE_URL}/go/', 'GET'
        ).content

        # Using the standard string methods
        # instead of the expensive xml parsing
        head = b'<head>'
        headtag = loginpage.find(head)
        headend = loginpage.find(b'</head>', headtag + len(head))

        # Some checks
        if headtag < 0 or headend < 0:
            pagehead = loginpage
            log.warning(
                'Unable to find <head> tag, parsing the whole page'
            )

        else:
            # Extracting <head> content
            headtag = headtag + len(head)
            pagehead = loginpage[headtag:headend]

        js_code: Optional[List[Any]] = None

        try:
            text = pagehead.decode('utf-8', 'replace')
            js_code = re.findall(ARROW_FN_REGEX, text)

            token_func = js_code[0]
            if len(js_code) > 1:
                token_func = js_code[1]

            js = atjsparse.get_interpreter()
            js.exec_js(token_func)
            self.token = js['AJAX_TOKEN']

        except (IndexError, TypeError) as err:

            log.warning('---')
            log.warning('Unable to parse AJAX_TOKEN!')
            log.warning('Please, insert the info below')
            log.warning('to the GitHub issue description:')
            log.warning('---')

            log.warning('JavaScript: %s', js_code)
            log.warning(
                'All script tags: %s',
                re.findall(SCRIPT_TAG_REGEX, pagehead)
            )
            log.warning('---')

            raise TokenError(
                'Unable to parse TOKEN from the page'
            ) from err

        return self.token

    def generate_sec(self) -> str:
        """Generates Aternos SEC token which
        is also needed for most API requests

        Returns:
            Random SEC `key:value` string
        """

        randkey = self.generate_sec_part()
        randval = self.generate_sec_part()
        self.sec = f'{randkey}:{randval}'
        self.session.cookies.set(
            f'ATERNOS_SEC_{randkey}', randval,
            domain='aternos.org'
        )

        return self.sec

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
            timeout: int = 4) -> requests.Response:
        """Sends a request to Aternos API bypass Cloudflare

        Args:
            url (str): Request URL
            method (str): Request method, must be GET or POST
            params (Optional[Dict[Any, Any]], optional): URL parameters
            data (Optional[Dict[Any, Any]], optional): POST request data,
                if the method is GET, this dict will be combined with params
            headers (Optional[Dict[Any, Any]], optional): Custom headers
            reqcookies (Optional[Dict[Any, Any]], optional):
                Cookies only for this request
            sendtoken (bool, optional): If the ajax and SEC token
                should be sent
            retries (int, optional): How many times parser must retry
                connection to API bypass Cloudflare
            timeout (int, optional): Request timeout in seconds

        Raises:
            CloudflareError: When the parser has exceeded retries count
            NotImplementedError: When the specified method is not GET or POST

        Returns:
            API response
        """

        if retries <= 0:
            raise CloudflareError('Unable to bypass Cloudflare protection')

        try:
            self.atcookie = self.session.cookies['ATERNOS_SESSION']
        except KeyError:
            pass

        self.refresh_session()

        params = params or {}
        data = data or {}
        headers = headers or {}
        reqcookies = reqcookies or {}

        method = method or 'GET'
        method = method.upper().strip()
        if method not in ('GET', 'POST'):
            raise NotImplementedError('Only GET and POST are available')

        if sendtoken:
            params['TOKEN'] = self.token
            params['SEC'] = self.sec
            headers['X-Requested-With'] = 'XMLHttpRequest'

        # requests.cookies.CookieConflictError bugfix
        reqcookies['ATERNOS_SESSION'] = self.atcookie
        del self.session.cookies['ATERNOS_SESSION']

        if is_debug():

            reqcookies_dbg = {
                k: str(v or '')[:3]
                for k, v in reqcookies.items()
            }

            session_cookies_dbg = {
                k: str(v or '')[:3]
                for k, v in self.session.cookies.items()
            }

            log.debug('Requesting(%s)%s', method, url)
            log.debug('headers=%s', headers)
            log.debug('params=%s', params)
            log.debug('data=%s', data)
            log.debug('req-cookies=%s', reqcookies_dbg)
            log.debug('session-cookies=%s', session_cookies_dbg)

        if method == 'POST':
            sendreq = partial(
                self.session.post,
                params=params,
                data=data,
            )
        else:
            sendreq = partial(
                self.session.get,
                params={**params, **data},
            )

        req = sendreq(
            url,
            headers=headers,
            cookies=reqcookies,
            timeout=timeout,
        )

        resp_type = req.headers.get('content-type', '')
        html_type = resp_type.find('text/html') != -1
        cloudflare = req.status_code == 403

        if html_type and cloudflare:
            log.info('Retrying to bypass Cloudflare')
            time.sleep(0.3)
            return self.request_cloudflare(
                url, method,
                params, data,
                headers, reqcookies,
                sendtoken, retries - 1
            )

        log.debug('AternosConnect received: %s', req.text[:65])
        log.info(
            '%s completed with %s status',
            method, req.status_code
        )

        if req.status_code == 402:
            raise AternosPermissionError

        req.raise_for_status()
        return req

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

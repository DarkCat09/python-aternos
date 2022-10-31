"""Stores API connection session and sends requests"""

import re
import time
import secrets
import logging
from functools import partial

from typing import Optional
from typing import List, Dict, Any

import requests

from cloudscraper import CloudScraper

from . import atjsparse
from .aterrors import TokenError
from .aterrors import CloudflareError
from .aterrors import AternosPermissionError

REQUA = \
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ' \
    '(KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36 OPR/85.0.4341.47'

ARROW_FN_REGEX = r'\(\(\)(.*?)\)\(\);'
SCRIPT_TAG_REGEX = (
    rb'<script type=([\'"]?)text/javascript\1>.+?</script>'
)


class AternosConnect:

    """Class for sending API requests,
    bypassing Cloudflare and parsing responses"""

    def __init__(self) -> None:

        self.cf_init = partial(CloudScraper)
        self.session = self.cf_init()
        self.sec = ''
        self.token = ''

    def add_args(self, **kwargs) -> None:
        """Pass arguments to CloudScarper
        session object __init__
        if kwargs is not empty

        Args:
            **kwargs: Keyword arguments
        """

        if len(kwargs) < 1:
            logging.debug('**kwargs is empty')
            return

        logging.debug('New args for CloudScraper: %s', kwargs)
        self.cf_init = partial(CloudScraper, **kwargs)
        self.refresh_session()

    def clear_args(self) -> None:
        """Clear CloudScarper object __init__ arguments
        which was set using add_args method"""

        logging.debug('Creating session object with no keywords')
        self.cf_init = partial(CloudScraper)
        self.refresh_session()

    def refresh_session(self) -> None:
        """Creates a new CloudScraper
        session object and copies all cookies.
        Required for bypassing Cloudflare"""

        old_cookies = self.session.cookies
        self.session = self.cf_init()
        self.session.cookies.update(old_cookies)
        del old_cookies

    def parse_token(self) -> str:
        """Parses Aternos ajax token that
        is needed for most requests

        Raises:
            RuntimeWarning: If the parser can not
                find `<head>` tag in HTML response
            TokenError: If the parser is unable
                to extract ajax token from HTML

        Returns:
            Aternos ajax token
        """

        loginpage = self.request_cloudflare(
            'https://aternos.org/go/', 'GET'
        ).content

        # Using the standard string methods
        # instead of the expensive xml parsing
        head = b'<head>'
        headtag = loginpage.find(head)
        headend = loginpage.find(b'</head>', headtag + len(head))

        # Some checks
        if headtag < 0 or headend < 0:
            pagehead = loginpage
            logging.warning(
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

            ctx = atjsparse.exec_js(token_func)
            self.token = ctx.window['AJAX_TOKEN']

        except (IndexError, TypeError) as err:

            logging.warning('---')
            logging.warning('Unable to parse AJAX_TOKEN!')
            logging.warning('Please, insert the info below')
            logging.warning('to the GitHub issue description:')
            logging.warning('---')

            logging.warning('JavaScript: %s', js_code)
            logging.warning(
                'All script tags: %s',
                re.findall(SCRIPT_TAG_REGEX, pagehead)
            )
            logging.warning('---')

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

        randkey = secrets.token_hex(8)
        randval = secrets.token_hex(8)
        self.sec = f'{randkey}:{randval}'
        self.session.cookies.set(
            f'ATERNOS_SEC_{randkey}', randval,
            domain='aternos.org'
        )

        return self.sec

    def request_cloudflare(
            self, url: str, method: str,
            params: Optional[Dict[Any, Any]] = None,
            data: Optional[Dict[Any, Any]] = None,
            headers: Optional[Dict[Any, Any]] = None,
            reqcookies: Optional[Dict[Any, Any]] = None,
            sendtoken: bool = False,
            retry: int = 5) -> requests.Response:
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
            retry (int, optional): How many times parser must retry
                connection to API bypass Cloudflare

        Raises:
            CloudflareError: When the parser has exceeded retries count
            NotImplementedError: When the specified method is not GET or POST

        Returns:
            API response
        """

        if retry <= 0:
            raise CloudflareError('Unable to bypass Cloudflare protection')

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
        reqcookies['ATERNOS_SESSION'] = self.atsession
        del self.session.cookies['ATERNOS_SESSION']

        reqcookies_dbg = {
            k: str(v or '')[:3]
            for k, v in reqcookies.items()
        }

        session_cookies_dbg = {
            k: str(v or '')[:3]
            for k, v in self.session.cookies.items()
        }

        logging.debug('Requesting(%s)%s', method, url)
        logging.debug('headers=%s', headers)
        logging.debug('params=%s', params)
        logging.debug('data=%s', data)
        logging.debug('req-cookies=%s', reqcookies_dbg)
        logging.debug('session-cookies=%s', session_cookies_dbg)

        if method == 'POST':
            sendreq = partial(
                self.session.post,
                params=params,
                data=data
            )
        else:
            sendreq = partial(
                self.session.get,
                params={**params, **data}
            )

        req = sendreq(
            url,
            headers=headers,
            cookies=reqcookies
        )

        resp_type = req.headers.get('content-type', '')
        html_type = resp_type.find('text/html') != -1
        cloudflare = req.status_code == 403

        if html_type and cloudflare:
            logging.info('Retrying to bypass Cloudflare')
            time.sleep(0.2)
            return self.request_cloudflare(
                url, method,
                params, data,
                headers, reqcookies,
                sendtoken, retry - 1
            )

        logging.debug('AternosConnect received: %s', req.text[:65])
        logging.info(
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

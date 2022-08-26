"""Stores API connection session and sends requests"""

import re
import time
import random
import logging
from functools import partial

from typing import Optional, Union
from typing import Dict, Any

import requests

from cloudscraper import CloudScraper

from . import atjsparse
from .aterrors import TokenError
from .aterrors import CloudflareError
from .aterrors import AternosPermissionError

REQUA = \
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ' \
    '(KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36 OPR/85.0.4341.47'


class AternosConnect:

    """Class for sending API requests
    bypass Cloudflare and parsing responses"""

    def __init__(self) -> None:

        self.session = CloudScraper()
        self.sec = ''
        self.token = ''

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
            raise RuntimeWarning(
                'Unable to find <head> tag, parsing the whole page'
            )

        # Extracting <head> content
        headtag = headtag + len(head)
        pagehead = loginpage[headtag:headend]

        try:
            text = pagehead.decode('utf-8', 'replace')
            js_code = re.findall(r'\(\(\)(.*?)\)\(\);', text)

            token_func = js_code[0]
            if len(js_code) > 1:
                token_func = js_code[1]

            ctx = atjsparse.exec_js(token_func)
            self.token = ctx.window['AJAX_TOKEN']

        except (IndexError, TypeError) as err:
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

        randkey = self.generate_aternos_rand()
        randval = self.generate_aternos_rand()
        self.sec = f'{randkey}:{randval}'
        self.session.cookies.set(
            f'ATERNOS_SEC_{randkey}', randval,
            domain='aternos.org'
        )

        return self.sec

    def generate_aternos_rand(self, randlen: int = 16) -> str:

        """Generates a random string using
        Aternos algorithm from main.js file

        Args:
            randlen (int, optional): Random string length

        Returns:
            Random string for SEC token
        """

        # a list with randlen+1 empty strings:
        # generate a string with spaces,
        # then split it by space
        rand_arr = (' ' * (randlen + 1)).split(' ')

        rand = random.random()
        rand_alphanum = self.convert_num(rand, 36) + ('0' * 17)

        return rand_alphanum[:18].join(rand_arr)[:randlen]

    def convert_num(
            self, num: Union[int, float, str],
            base: int, frombase: int = 10) -> str:

        """Converts an integer to specified base

        Args:
            num (Union[int,float,str]): Integer in any base to convert.
                If it is a float starting with `0.`,
                zero and point will be removed to get int
            base (int): New base
            frombase (int, optional): Given number base

        Returns:
            Number converted to a specified base
        """

        if isinstance(num, str):
            num = int(num, frombase)

        if isinstance(num, float):
            sliced = str(num)[2:]
            num = int(sliced)

        symbols = '0123456789abcdefghijklmnopqrstuvwxyz'
        basesym = symbols[:base]
        result = ''
        while num > 0:
            rem = num % base
            result = str(basesym[rem]) + result
            num //= base
        return result

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

        old_cookies = self.session.cookies
        self.session = CloudScraper()
        self.session.cookies.update(old_cookies)

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

        logging.debug(f'Requesting({method}){url}')
        logging.debug(f'headers={headers}')
        logging.debug(f'params={params}')
        logging.debug(f'data={data}')
        logging.debug(f'req-cookies={reqcookies}')
        logging.debug(f'session-cookies={self.session.cookies}')

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

        logging.debug('AternosConnect received: ' + req.text[:65])
        logging.info(
            f'{method} completed with {req.status_code} status'
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

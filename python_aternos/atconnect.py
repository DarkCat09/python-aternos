import re
import time
import random
import lxml.html
from requests import Response
from cloudscraper import CloudScraper
from typing import Optional, Union

from . import aterrors

#TEST
from py_mini_racer import MiniRacer
import base64

presettings = """ 
let window = {1: null, 2: null, AJAX_TOKEN: null}; 
let i = 1; 
function __log() { return {win_var: window["AJAX_TOKEN"], 1: window[1], 2: window[2]} }; 
function atob(arg) {window[i++] = arg;}; 
""" 
postsettings = """__log();"""


REQGET = 0
REQPOST = 1
REQUA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Goanna/4.8 Firefox/68.0 PaleMoon/29.4.0.2'

class AternosConnect:

    def __init__(self) -> None:

        pass

    def parse_token(self, response:Optional[Union[str,bytes]]=None) -> str:

        if response == None:
            loginpage = self.request_cloudflare(
                f'https://aternos.org/go/', REQGET
            ).content
            pagetree = lxml.html.fromstring(loginpage)
        else:
            pagetree = lxml.html.fromstring(response)

        try:
            # fetch text
            pagehead = pagetree.head
            text = pagehead.text_content()
            #print(text)

            #search
            token_js_func = text[
                text.index("const COOKIE_PREFIX = \"ATERNOS\";") +
                len("const COOKIE_PREFIX = \"ATERNOS\";")       :
                text.index("(function(i,s,o,g,r,a,m)")
            ].strip()
            print(token_js_func)


            # run js
            ctx = MiniRacer()
            result = ctx.eval(presettings + token_js_func) 
            result = ctx.call('__log')
            
            print(result)
    
            if 'win_var' in result and result['win_var']:
                result = result['win_var']
            elif '1' in result and ('2' in result and not result['2']):
                result = base64.standard_b64decode(result['1'])
            else:
                result = base64.standard_b64decode(result['2'])  


            print(result)
            self.token = result 
        
            """
            self.token = re.search(
                r'const\s+AJAX_TOKEN\s*=\s*["\'](\w+)["\']',
                text
            )[1]
            """
        except (IndexError, TypeError):
            raise aterrors.AternosCredentialsError(
                'Unable to parse TOKEN from the page'
            )

        return self.token

    def generate_sec(self) -> str:

        randkey = self.generate_aternos_rand()
        randval = self.generate_aternos_rand()
        self.sec = f'{randkey}:{randval}'
        self.session.cookies.set(
            f'ATERNOS_SEC_{randkey}', randval,
            domain='aternos.org'
        )

        return self.sec

    def generate_aternos_rand(self, randlen:int=16) -> str:

        rand_arr = []
        for i in range(randlen+1):
            rand_arr.append('')

        rand_alphanum = \
            self.convert_num(random.random(),36) + \
            '00000000000000000'
        return (rand_alphanum[2:18].join(rand_arr)[:randlen])

    def convert_num(self, num:Union[int,float], base:int) -> str:

        result = ''
        while num > 0:
            result = str(num % base) + result
            num //= base
        return result

    def request_cloudflare(
        self, url:str, method:int,
        retries:int=10,
        params:Optional[dict]=None,
        data:Optional[dict]=None,
        headers:Optional[dict]=None,
        reqcookies:Optional[dict]=None,
        sendtoken:bool=False) -> Response:

        cftitle = '<title>Please Wait... | Cloudflare</title>'

        if sendtoken:
            if params == None:
                params = {}
            params['SEC'] = self.sec
            params['TOKEN'] = self.token

        if headers == None:
            headers = {}
        headers['User-Agent'] = REQUA

        try:
            cookies = self.session.cookies
        except AttributeError:
            cookies = None

        self.session = CloudScraper()
        if cookies != None:
            self.session.cookies = cookies

        if method == REQPOST:
            req = self.session.post(
                url,
                data=data,
                headers=headers,
                cookies=reqcookies
            )
        else:
            req = self.session.get(
                url,
                params=params,
                headers=headers,
                cookies=reqcookies
            )

        countdown = retries
        while cftitle in req.text \
        and (countdown > 0):

            self.session = CloudScraper()
            if cookies != None:
                self.session.cookies = cookies
            if reqcookies != None:
                for cookiekey in reqcookies:
                    self.session.cookies.set(cookiekey, reqcookies[cookiekey])

            time.sleep(1)
            if method == REQPOST:
                req = self.session.post(
                    url,
                    data=data,
                    headers=headers,
                    cookies=reqcookies
                )
            else:
                req = self.session.get(
                    url,
                    params=params,
                    headers=headers,
                    cookies=reqcookies
                )
            countdown -= 1

        return req

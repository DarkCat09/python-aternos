import re
import random
import logging
from requests import Response
from cloudscraper import CloudScraper
from typing import Optional, Union

from . import atjsparse
from .aterrors import TokenError, CloudflareError

REQUA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36 OPR/85.0.4341.47'

class AternosConnect:

	"""
	Class for sending API requests bypass Cloudflare
	and parsing responses"""

	def __init__(self) -> None:

		self.session = CloudScraper()
		self.atsession = ''

	def parse_token(self) -> str:

		"""Parses Aternos ajax token that
		is needed for most requests

		:raises RuntimeWarning: If the parser
		can not find <head> tag in HTML response
		:raises CredentialsError: If the parser
		is unable to extract ajax token in HTML
		:return: Aternos ajax token
		:rtype: str
		"""

		loginpage = self.request_cloudflare(
			f'https://aternos.org/go/', 'GET'
		).content

		# Using the standard string methods
		# instead of the expensive xml parsing
		head = b'<head>'
		headtag = loginpage.find(head)
		headend = loginpage.find(b'</head>', headtag + len(head))

		# Some checks
		if headtag < 0 or headend < 0:
			pagehead = loginpage
			raise RuntimeWarning('Unable to find <head> tag, parsing the whole page')

		# Extracting <head> content
		headtag = headtag + len(head)
		pagehead = loginpage[headtag:headend]

		try:
			text = pagehead.decode('utf-8', 'replace')
			js_code = re.findall(r'\(\(\)(.*?)\)\(\);', text)
			token_func = js_code[1] if len(js_code) > 1 else js_code[0]

			ctx = atjsparse.exec(token_func)
			self.token = ctx.window['AJAX_TOKEN']

		except (IndexError, TypeError):
			raise TokenError(
				'Unable to parse TOKEN from the page'
			)

		return self.token

	def generate_sec(self) -> str:

		"""Generates Aternos SEC token which
		is also needed for most API requests

		:return: Random SEC key:value string
		:rtype: str
		"""

		randkey = self.generate_aternos_rand()
		randval = self.generate_aternos_rand()
		self.sec = f'{randkey}:{randval}'
		self.session.cookies.set(
			f'ATERNOS_SEC_{randkey}', randval,
			domain='aternos.org'
		)

		return self.sec

	def generate_aternos_rand(self, randlen:int=16) -> str:

		"""Generates a random string using
		Aternos algorithm from main.js file

		:param randlen: Random string length, defaults to 16
		:type randlen: int, optional
		:return: Random string for SEC token
		:rtype: str
		"""

		# a list with randlen+1 empty strings:
		# generate a string with spaces,
		# then split it by space
		rand_arr = (' ' * (randlen+1)).split(' ')

		rand = random.random()
		rand_alphanum = self.convert_num(rand, 36) + ('0' * 17)

		return (rand_alphanum[:18].join(rand_arr)[:randlen])

	def convert_num(
		self, num:Union[int,float,str],
		base:int, frombase:int=10) -> str:

		"""Converts an integer to specified base

		:param num: Integer in any base to convert.
		If it is a float started with `0,`,
		zero and comma will be removed to get int
		:type num: Union[int,float,str]
		:param base: New base
		:type base: int
		:param frombase: Given number base, defaults to 10
		:type frombase: int, optional
		:return: Number converted to a specified base
		:rtype: str
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
		self, url:str, method:str,
		params:Optional[dict]=None, data:Optional[dict]=None,
		headers:Optional[dict]=None, reqcookies:Optional[dict]=None,
		sendtoken:bool=False, redirect:bool=True, retry:int=3) -> Response:

		"""Sends a request to Aternos API bypass Cloudflare

		:param url: Request URL
		:type url: str
		:param method: Request method, must be GET or POST
		:type method: str
		:param params: URL parameters, defaults to None
		:type params: Optional[dict], optional
		:param data: POST request data, if the method is GET,
		this dict will be combined with params, defaults to None
		:type data: Optional[dict], optional
		:param headers: Custom headers, defaults to None
		:type headers: Optional[dict], optional
		:param reqcookies: Cookies only for this request, defaults to None
		:type reqcookies: Optional[dict], optional
		:param sendtoken: If the ajax and SEC token
		should be sent, defaults to False
		:type sendtoken: bool, optional
		:param redirect: If requests lib should follow
		Location header in 3xx responses, defaults to True
		:type redirect: bool, optional
		:param retry: How many times parser must retry
		connection to API bypass Cloudflare, defaults to 3
		:type retry: int, optional
		:raises CloudflareError:
		When the parser has exceeded retries count
		:raises NotImplementedError:
		When the specified method is not GET or POST
		:return: API response
		:rtype: requests.Response
		"""

		if retry <= 0:
			raise CloudflareError('Unable to bypass Cloudflare protection')

		try:
			self.atsession = self.session.cookies['ATERNOS_SESSION']
		except KeyError:
			pass

		method = method or 'GET'
		method = method.upper().strip()
		if method not in ('GET', 'POST'):
			raise NotImplementedError('Only GET and POST are available')

		headers = headers or {}
		params = params or {}
		data = data or {}
		reqcookies = reqcookies or {}

		if sendtoken:
			params['TOKEN'] = self.token
			params['SEC'] = self.sec
			headers['X-Requested-With'] = 'XMLHttpRequest'

		# requests.cookies.CookieConflictError bugfix
		reqcookies['ATERNOS_SESSION'] = self.atsession
		del self.session.cookies['ATERNOS_SESSION']

		logging.debug(f'Requesting({method})' + url)
		logging.debug('headers=' + str(headers))
		logging.debug('params=' + str(params))
		logging.debug('data=' + str(data))
		logging.debug('req-cookies=' + str(reqcookies))
		logging.debug('session-cookies=' + str(self.session.cookies))
		
		if method == 'POST':
			req = self.session.post(
				url, data=data, params=params,
				headers=headers, cookies=reqcookies,
				allow_redirects=redirect
			)
		else:
			req = self.session.get(
				url, params={**params, **data},
				headers=headers, cookies=reqcookies,
				allow_redirects=redirect
			)
		
		if '<title>Please Wait... | Cloudflare</title>' in req.text:
			logging.info('Retrying to bypass Cloudflare')
			self.request_cloudflare(
				url, method,
				params, data,
				headers, reqcookies,
				sendtoken, redirect,
				retry - 1
			)
		
		logging.info(
			f'{method} completed with {req.status_code} status'
		)

		return req

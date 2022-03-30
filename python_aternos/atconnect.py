import re
import random
import logging
import lxml.html
from requests import Response
from cloudscraper import CloudScraper
from typing import Optional, Union

from . import atjsparse
from .aterrors import CredentialsError

REQUA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Goanna/4.8 Firefox/68.0 PaleMoon/29.4.0.2'

class AternosConnect:

	def __init__(self) -> None:

		self.session = CloudScraper()
		self.atsession = ''

	def parse_token(self) -> str:

		loginpage = self.request_cloudflare(
			f'https://aternos.org/go/', 'GET'
		).content
		pagetree = lxml.html.fromstring(loginpage)

		try:
			pagehead = pagetree.head
			text = pagehead.text_content()

			js_code = re.findall(r'\(\(\)(.*?)\)\(\);', text)
			token_func = js_code[1] if len(js_code) > 1 else js_code[0]

			ctx = atjsparse.exec(token_func)
			self.token = ctx.window['AJAX_TOKEN']

		except (IndexError, TypeError):
			raise CredentialsError(
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
		sendtoken:bool=False, redirect:bool=True) -> Response:

		try:
			self.atsession = self.session.cookies['ATERNOS_SESSION']
		except KeyError:
			pass

		if method not in ('GET', 'POST'):
			raise NotImplementedError('Only GET and POST are available')

		params = params or {}
		data = data or {}
		headers = headers or {}
		reqcookies = reqcookies or {}
		headers['User-Agent'] = REQUA

		if sendtoken:
			params['TOKEN'] = self.token
			params['SEC'] = self.sec

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
		
		logging.info(
			f'{method} completed with {req.status_code} status'
		)

		with open('debug.html', 'wb') as f:
			f.write(req.content)

		return req

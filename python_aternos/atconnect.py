import re
import time
import random
import lxml.html
from requests import Response
from cloudscraper import CloudScraper
from typing import Optional, Union

from . import atjsparse
from .aterrors import CredentialsError, CloudflareError

REQUA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Goanna/4.8 Firefox/68.0 PaleMoon/29.4.0.2'

class AternosConnect:

	def __init__(self) -> None:

		pass

	def parse_token(self, response:Optional[Union[str,bytes]]=None) -> str:

		if response == None:
			loginpage = self.request_cloudflare(
				f'https://aternos.org/go/', 'GET'
			).content
			pagetree = lxml.html.fromstring(loginpage)
		else:
			pagetree = lxml.html.fromstring(response)

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

		rand_arr = []
		for i in range(randlen+1):
			rand_arr.append('')

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
		self, url:str, method:str, retries:int=10,
		params:Optional[dict]=None, data:Optional[dict]=None,
		headers:Optional[dict]=None, reqcookies:Optional[dict]=None,
		sendtoken:bool=False, redirect:bool=True) -> Response:

		cftitle = '<title>Please Wait... | Cloudflare</title>'

		if params == None:
			params = {}

		if headers == None:
			headers = {}
		headers['User-Agent'] = REQUA

		if sendtoken:
			url += f'?TOKEN={self.token}&SEC={self.sec}'

		try:
			cookies = self.session.cookies
		except AttributeError:
			cookies = None

		countdown = retries
		while True:

			self.session = CloudScraper()
			if cookies != None:
				self.session.cookies = cookies

			if reqcookies != None:
				for cookiekey in reqcookies:
					self.session.cookies.set(cookiekey, reqcookies[cookiekey])

			time.sleep(1)

			if method == 'POST':
				req = self.session.post(
					url, data=data, params=params,
					headers=headers, cookies=reqcookies,
					allow_redirects=redirect
				)
			else:
				req = self.session.get(
					url, params=params,
					headers=headers, cookies=reqcookies,
					allow_redirects=redirect
				)

			if not cftitle in req.text:
				break
			if not countdown > 0:
				raise CloudflareError(
					'The retries limit has been reached'
				)
			countdown -= 1

		return req

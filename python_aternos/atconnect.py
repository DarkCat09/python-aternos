import re
import time
import random
import lxml.html
from requests import Response
from cloudscraper import CloudScraper
from typing import Optional, Union

from . import aterrors

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
			pagehead = pagetree.head
			self.token = re.search(
				r'const\s+AJAX_TOKEN\s*=\s*["\'](\w+)["\']',
				pagehead.text_content()
			)[1]
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

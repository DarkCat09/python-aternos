import hashlib
import lxml.html
from typing import Optional, Union, List

from . import atserver
from . import atconnect
from . import aterrors

from .aterrors import AternosCredentialsError

class Client:

	def __init__(self, atconn:atconnect.AternosConnect) -> None:

		self.atconn = atconn

	@classmethod
	def from_hashed(cls, username:str, md5:str):

		atconn = atconnect.AternosConnect()
		atconn.parse_token()
		atconn.generate_sec()

		credentials = {
			'user': username,
			'password': md5
		}

		loginreq = atconn.request_cloudflare(
			f'https://aternos.org/panel/ajax/account/login.php',
			atconnect.REQPOST, data=credentials,
			sendtoken=True
		)

		if loginreq.cookies.get('ATERNOS_SESSION', None) == None:
			raise AternosCredentialsError(
				'Check your username and password'
			)

		return cls(atconn)

	@classmethod
	def from_credentials(cls, username:str, password:str):

		pswd_bytes = password.encode('utf-8')
		md5 = hashlib.md5(pswd_bytes).hexdigest().lower()

		return cls.from_hashed(username, md5)

	@classmethod
	def from_session(cls, session:str):
		
		atconn = atconnect.AternosConnect()
		atconn.session.cookies.set('ATERNOS_SESSION', session)
		atconn.parse_token()
		atconn.generate_sec()

		return cls(atconn)

	@staticmethod
	def google() -> str:

		atconn = atconnect.AternosConnect()
		auth = atconn.request_cloudflare(
			'https://aternos.org/auth/google-login',
			atconnect.REQGET, redirect=False
		)
		return auth.headers['Location']

	@property
	def servers(self) -> List[atserver.AternosServer]:
		serverspage = self.atconn.request_cloudflare(
			'https://aternos.org/servers/',
			atconnect.REQGET
		)
		serverstree = lxml.html.fromstring(serverspage.content)
		serverslist = serverstree.xpath('//div[contains(@class,"servers ")]/div')

		servers = []
		for server in serverslist:
			servid = server.xpath('./div[@class="server-body"]/@data-id')[0]
			servers.append(atserver.AternosServer(servid, self.atconn))

		return servers

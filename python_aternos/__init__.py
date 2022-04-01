import os
import re
import hashlib
import lxml.html
from typing import List

from .atserver import AternosServer
from .atconnect import AternosConnect
from .aterrors import CredentialsError

__all__ = ['Client', 'atconf', 'atconnect', 'aterrors', 'atfile', 'atfm', 'atjsparse', 'atplayers', 'atserver', 'atwss']

class Client:

	def __init__(self, atconn:atconnect.AternosConnect) -> None:

		self.atconn = atconn

	@classmethod
	def from_hashed(cls, username:str, md5:str):

		atconn = AternosConnect()
		atconn.parse_token()
		atconn.generate_sec()

		credentials = {
			'user': username,
			'password': md5
		}

		loginreq = atconn.request_cloudflare(
			f'https://aternos.org/panel/ajax/account/login.php',
			'POST', data=credentials, sendtoken=True
		)

		if 'ATERNOS_SESSION' not in loginreq.cookies:
			raise CredentialsError(
				'Check your username and password'
			)

		return cls(atconn)

	@classmethod
	def from_credentials(cls, username:str, password:str):

		md5 = Client.md5encode(password)
		return cls.from_hashed(username, md5)

	@classmethod
	def from_session(cls, session:str):
		
		atconn = AternosConnect()
		atconn.session.cookies['ATERNOS_SESSION'] = session
		atconn.parse_token()
		atconn.generate_sec()

		return cls(atconn)
	
	@classmethod
	def restore_session(cls, file:str='~/.aternos'):

		file = os.path.expanduser(file)
		with open(file, 'rt') as f:
			session = f.read().strip()
		return cls.from_session(session)
	
	@staticmethod
	def md5encode(passwd:str) -> str:

		encoded = hashlib.md5(passwd.encode('utf-8'))
		return encoded.hexdigest().lower()
	
	def save_session(self, file:str='~/.aternos') -> None:

		file = os.path.expanduser(file)
		with open(file, 'wt') as f:
			f.write(self.atconn.atsession)

	def list_servers(self) -> List[AternosServer]:

		serverspage = self.atconn.request_cloudflare(
			'https://aternos.org/servers/', 'GET'
		)
		serverstree = lxml.html.fromstring(serverspage.content)
		serverslist = serverstree.xpath('//div[contains(@class,"servers ")]/div')

		servers = []
		for server in serverslist:
			servid = server.xpath('./div[@class="server-body"]/@data-id')[0]
			servers.append(AternosServer(servid, self.atconn))

		return servers
	
	def get_server(self, servid:str) -> AternosServer:

		return AternosServer(servid, self.atconn)
	
	def change_username(self, value:str) -> None:

		self.atconn.request_cloudflare(
			'https://aternos.org/panel/ajax/account/username.php',
			'POST', data={'username': value}
		)
	
	def change_email(self, value:str) -> None:

		email = re.compile(r'^[A-Za-z0-9\-_+.]+@[A-Za-z0-9\-_+.]+\.[A-Za-z0-9\-]+$|^$')
		if not email.match(value):
			raise ValueError('Invalid e-mail!')

		self.atconn.request_cloudflare(
			'https://aternos.org/panel/ajax/account/email.php',
			'POST', data={'email': value}
		)
	
	def change_password(self, old:str, new:str) -> None:

		old = Client.md5encode(old)
		new = Client.md5encode(new)
		self.atconn.request_cloudflare(
			'https://aternos.org/panel/ajax/account/password.php',
			'POST', data={
				'oldpassword': old,
				'newpassword': new
			}
		)

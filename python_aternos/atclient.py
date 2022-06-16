import os
import re
import hashlib
import lxml.html
from typing import List

from .atserver import AternosServer
from .atconnect import AternosConnect
from .aterrors import CredentialsError

class Client:

	"""Aternos API Client class whose object contains user's auth data

	:param atconn: :class:`python_aternos.atconnect.AternosConnect` instance with initialized Aternos session
	:type atconn: python_aternos.atconnect.AternosConnect
	"""	

	def __init__(self, atconn:AternosConnect) -> None:

		self.atconn = atconn

	@classmethod
	def from_hashed(cls, username:str, md5:str):

		"""Log in to Aternos with a username and a hashed password

		:param username: Your username
		:type username: str
		:param md5: Your password hashed with MD5
		:type md5: str
		:raises CredentialsError: If the API doesn't return a valid session cookie
		:return: Client instance
		:rtype: python_aternos.Client
		"""		

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

		"""Log in to Aternos with a username and a plain password

		:param username: Your username
		:type username: str
		:param password: Your password without any encryption
		:type password: str
		:return: Client instance
		:rtype: python_aternos.Client
		"""		

		md5 = Client.md5encode(password)
		return cls.from_hashed(username, md5)

	@classmethod
	def from_session(cls, session:str):

		"""Log in to Aternos using a session cookie value

		:param session: Value of ATERNOS_SESSION cookie
		:type session: str
		:return: Client instance
		:rtype: python_aternos.Client
		"""		
		
		atconn = AternosConnect()
		atconn.session.cookies['ATERNOS_SESSION'] = session
		atconn.parse_token()
		atconn.generate_sec()

		return cls(atconn)
	
	@classmethod
	def restore_session(cls, file:str='~/.aternos'):

		"""Log in to Aternos using a saved ATERNOS_SESSION cookie

		:param file: File where a session cookie was saved, deafults to ~/.aternos
		:type file: str, optional
		:return: Client instance
		:rtype: python_aternos.Client
		"""		

		file = os.path.expanduser(file)
		with open(file, 'rt') as f:
			session = f.read().strip()
		return cls.from_session(session)
	
	@staticmethod
	def md5encode(passwd:str) -> str:

		"""Encodes the given string with MD5

		:param passwd: String to encode
		:type passwd: str
		:return: Hexdigest hash of the string in lowercase
		:rtype: str
		"""		

		encoded = hashlib.md5(passwd.encode('utf-8'))
		return encoded.hexdigest().lower()
	
	def save_session(self, file:str='~/.aternos') -> None:

		"""Saves an ATERNOS_SESSION cookie to a file

		:param file: File where a session cookie must be saved, defaults to ~/.aternos
		:type file: str, optional
		"""		

		file = os.path.expanduser(file)
		with open(file, 'wt') as f:
			f.write(self.atconn.atsession)

	def list_servers(self) -> List[AternosServer]:

		"""Parses a list of your servers from Aternos website

		:return: List of :class:`python_aternos.atserver.AternosServer` objects
		:rtype: list
		"""		

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

		"""Creates a server object from the server ID.
		Use this instead of list_servers if you know the ID to save some time.

		:return: :class:`python_aternos.atserver.AternosServer` object
		:rtype: python_aternos.atserver.AternosServer
		"""		

		return AternosServer(servid, self.atconn)
	
	def change_username(self, value:str) -> None:

		"""Changes a username in your Aternos account

		:param value: New username
		:type value: str
		"""		

		self.atconn.request_cloudflare(
			'https://aternos.org/panel/ajax/account/username.php',
			'POST', data={'username': value}
		)
	
	def change_email(self, value:str) -> None:

		"""Changes an e-mail in your Aternos account

		:param value: New e-mail
		:type value: str
		:raises ValueError: If an invalid e-mail address is passed to the function
		"""		

		email = re.compile(r'^[A-Za-z0-9\-_+.]+@[A-Za-z0-9\-_+.]+\.[A-Za-z0-9\-]+$|^$')
		if not email.match(value):
			raise ValueError('Invalid e-mail!')

		self.atconn.request_cloudflare(
			'https://aternos.org/panel/ajax/account/email.php',
			'POST', data={'email': value}
		)
	
	def change_password(self, old:str, new:str) -> None:

		"""Changes a password in your Aternos account

		:param old: Old password
		:type old: str
		:param new: New password
		:type new: str
		"""		

		old = Client.md5encode(old)
		new = Client.md5encode(new)
		self.atconn.request_cloudflare(
			'https://aternos.org/panel/ajax/account/password.php',
			'POST', data={
				'oldpassword': old,
				'newpassword': new
			}
		)

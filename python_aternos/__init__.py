import hashlib
import lxml.html
from typing import Optional, List

from . import atserver
from . import atconnect
from . import aterrors

class Client:

	def __init__(
		self, username:str,
		md5:Optional[str]=None,
		password:Optional[str]=None) -> None:

		if (password == None) and (md5 == None):
			raise AttributeError('Password was not specified')

		if (password != None):
			self.__init__(
				username,
				md5=hashlib.md5(password.encode('utf-8'))\
				.hexdigest().lower()
			)
			return

		self.atconn = atconnect.AternosConnect()

		self.token = self.atconn.parse_token()
		self.sec = self.atconn.generate_sec()

		self.credentials = {
			'user': username,
			'password': md5
		}

		loginreq = self.atconn.request_cloudflare(
			f'https://aternos.org/panel/ajax/account/login.php?' + \
			f'SEC={self.sec}&TOKEN={self.token}',
			atconnect.REQPOST, data=self.credentials
		)

		if loginreq.cookies.get('ATERNOS_SESSION', None) == None:
			raise aterrors.AternosCredentialsError(
				'Check your username and password'
			)

	@property
	def servers(self) -> List[atserver.AternosServer]:
		serverspage = self.atconn.request_cloudflare(
			'https://aternos.org/servers/',
			atconnect.REQGET
		)
		serverstree = lxml.html.fromstring(serverspage.content)
		serverslist = serverstree.xpath('//div[@class="servers"]/div')

		servers = []
		for server in serverslist:
			servid = server.xpath('./div[@class="server-body"]/@data-id')[0]
			servers.append(atserver.AternosServer(servid, self.atconn))

		return servers

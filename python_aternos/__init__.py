import hashlib
import lxml.html
from typing import Optional, Union, List

from . import atserver
from . import atconnect
from . import aterrors
from . import client_secrets

class Client:

	def __init__(self, atconn:atconnect.AternosConnect) -> None:

		self.atconn = atconn

		# if google:
		# 	flow = Flow.from_client_config\
		# 	(
		# 		json.loads(
		# 			base64.standard_base64decode(client_secrets.CSJSON)
		# 		),
		# 		scopes=['openid', 'email']
		# 	)
		# 	# localhost:8764
		# 	flow.run_local_server(port=8764, open_browser=False)

	@classmethod
	def from_hashed(cls, username:str, md5:str):

		atconn = atconnect.AternosConnect()
		token = atconn.parse_token()
		sec = atconn.generate_sec()

		loginreq = self.atconn.request_cloudflare(
			f'https://aternos.org/panel/ajax/account/login.php',
			atconnect.REQPOST, data=self.credentials,
			sendtoken=True
		)

		if loginreq.cookies.get('ATERNOS_SESSION', None) == None:
			raise aterrors.AternosCredentialsError(
				'Check your username and password'
			)

		cls(atconn)

	@classmethod
	def from_credentials(cls, username:str, password:str):
		cls.from_hashed(
			username,
			hashlib.md5(password.encode('utf-8'))\
			.hexdigest().lower()
		)

	@classmethod
	def with_google(cls):
		pass

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

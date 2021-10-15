import re
import json
import lxml.html
from requests import Response
from typing import Optional, Dict

from . import atconnect
from . import aterrors
from . import atfm
from . import atconf
from . import atplayers

SOFTWARE_JAVA = 0
SOFTWARE_BEDROCK = 1

PLAYERS_ALLOWED = 'whitelist'
PLAYERS_OPS = 'ops'
PLAYERS_BANNED = 'banned-players'
PLAYERS_IPS = 'banned-ips'

STATUS_OFFLINE = 0
STATUS_ONLINE = 1
STATUS_LOADING = 2
STATUS_SHUTDOWN = 3
STATUS_ERROR = 7

class AternosServer:

	def __init__(self, servid:str, atconn:atconnect.AternosConnect) -> None:

		self.servid = servid
		self.atconn = atconn

		servreq = self.atserver_request(
			'https://aternos.org/server',
			atconnect.REQGET
		)
		servtree = lxml.html.fromstring(servreq.content)

		self._info = json.loads(
			re.search(
				r'var\s*lastStatus\s*=\s*({.*})',
				servtree.head.text_content()
			)[1]
		)

		self.atconn.parse_token(servreq.content)
		self.atconn.generate_sec()

	def start(self, accepteula:bool=True) -> None:

		startreq = self.atserver_request(
			'https://aternos.org/panel/ajax/start.php',
			atconnect.REQGET, sendtoken=True
		)
		startresult = startreq.json()

		if startresult['success']:
			return
		
		error = startresult['error']
		if error == 'eula' and accepteula:
			self.eula()
			self.start(accepteula=False)
		elif error == 'eula':
			raise aterrors.AternosServerStartError(
				'EULA was not accepted. Use start(accepteula=True)'
			)
		elif error == 'already':
			raise aterrors.AternosServerStartError(
				'Server is already running'
			)
		else:
			raise aterrors.AternosServerStartError(
				f'Unable to start server. Code: {error}'
			)

	def confirm(self) -> None:

		self.atserver_request(
			'https://aternos.org/panel/ajax/confirm.php',
			atconnect.REQGET, sendtoken=True
		)

	def stop(self) -> None:

		self.atserver_request(
			'https://aternos.org/panel/ajax/stop.php',
			atconnect.REQGET, sendtoken=True
		)

	def cancel(self) -> None:

		self.atserver_request(
			'https://aternos.org/panel/ajax/cancel.php',
			atconnect.REQGET, sendtoken=True
		)

	def restart(self) -> None:

		self.atserver_request(
			'https://aternos.org/panel/ajax/restart.php',
			atconnect.REQGET, sendtoken=True
		)

	def eula(self) -> None:

		self.atserver_request(
			'https://aternos.org/panel/ajax/eula.php',
			atconnect.REQGET, sendtoken=True
		)

	def files(self) -> atfm.AternosFileManager:

		return atfm.AternosFileManager(self)

	def config(self) -> atconf.AternosConfig:

		return atconf.AternosConfig(self)

	def players(self, lst:str) -> atplayers.AternosPlayersList:

		return atplayers.AternosPlayersList(lst, self)

	def atserver_request(
		self, url:str, method:int,
		params:Optional[dict]=None,
		data:Optional[dict]=None,
		headers:Optional[dict]=None,
		sendtoken:bool=False) -> Response:

		return self.atconn.request_cloudflare(
			url=url, method=method,
			params=params, data=data,
			headers=headers,
			reqcookies={
				'ATERNOS_SERVER': self.servid
			},
			sendtoken=sendtoken
		)

	@property
	def subdomain(self) -> str:
		atdomain = self.domain
		return atdomain[:atdomain.find('.')]

	@subdomain.setter
	def subdomain(self, value:str) -> None:
		self.atserver_request(
			'https://aternos.org/panel/ajax/options/subdomain.php',
			atconnect.REQGET, params={'subdomain': value}
		)

	@property
	def motd(self) -> str:
		return self._info['motd']

	@motd.setter
	def motd(self, value:str) -> None:
		self.atserver_request(
			'https://aternos.org/panel/ajax/options/motd.php',
			atconnect.REQPOST, data={'motd': value}
		)

	@property
	def address(self) -> str:
		return f'{self.domain}:{self.port}'
	
	@property
	def domain(self) -> str:
		return self._info['ip']

	@property
	def port(self) -> int:
		return self._info['port']

	@property
	def edition(self) -> int:
		soft_type = self._info['bedrock']
		if soft_type == True:
			return SOFTWARE_BEDROCK
		else:
			return SOFTWARE_JAVA

	@property
	def software(self) -> str:
		return self._info['software']
	
	@property
	def version(self) -> str:
		return self._info['version']

	@property
	def status(self) -> int:
		return int(self._info['status'])

	@property
	def ram(self) -> int:
		return int(self._info['ram'])

import enum
import re
import json
import lxml.html
import websockets
from requests import Response
from typing import Optional, Dict

from . import atconnect
from . import aterrors
from . import atfm
from . import atconf
from . import atplayers

JAVA = 0
BEDROCK = 1

class Lists(enum.Enum):
	whl = 'whitelist'
	ops = 'ops'
	ban = 'banned-players'
	ips = 'banned-ips'

class Status(enum.IntEnum):
	off = 0
	on = 1
	loading = 2
	shutdown = 3
	error = 7

class AternosServer:

	def __init__(
		self, servid:str,
		atconn:atconnect.AternosConnect,
		savelog:bool=True) -> None:

		self.servid = servid
		self.atconn = atconn
		self.savelog = savelog
		self.log = []

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
		self._ram = 0
		self._tps = 0

		self.atconn.parse_token(servreq.content)
		self.atconn.generate_sec()

	async def wss(self):

		session = self.atconn.session.cookies['ATERNOS_SESSION']
		headers = [
			('User-Agent', atconnect.REQUA),
			('Cookie',
				f'ATERNOS_SESSION={session}; ' + \
				f'ATERNOS_SERVER={self.servid}')
		]

		async with websockets.connect(
			'wss://aternos.org/hermes',
			extra_headers=headers
		) as websocket:
			while True:
				msg = await websocket.recv()
				r = json.loads(msg)

				if r['type'] == 'line' \
				and r['stream'] == 'console'\
				and self.savelog:
					self.log.append(r['data'])

				if r['type'] == 'heap':
					self._ram = r['data']['usage']

				if r['type'] == 'tick':
					aver = 1000 / r['data']['averageTickTime']
					self._tps = 20 if aver > 20 else aver

				if r['type'] == 'status':
					self._info = json.loads(r['message'])

	def start(self, headstart:bool=False, accepteula:bool=True) -> None:

		startreq = self.atserver_request(
			'https://aternos.org/panel/ajax/start.php',
			atconnect.REQGET, params={'headstart': int(headstart)},
			sendtoken=True
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

		elif error == 'wrongversion':
			raise aterrors.AternosServerStartError(
				'Incorrect software version installed'
			)

		elif error == 'file':
			raise aterrors.AternosServerStartError(
				'File server is unavailbale, view status.aternos.gmbh'
			)

		elif error == 'size':
			raise aterrors.AternosServerStartError(
				f'Available storage size is 4GB, ' + \
				f'your server used: {startresult["size"]}'
			)

		else:
			raise aterrors.AternosServerStartError(
				f'Unable to start server, code: {error}'
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

		correct = False
		for lsttype in Lists:
			if lsttype.value == lst:
				correct = True

		if not correct:
			raise AttributeError('Incorrect players list type! Use Lists enum')

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
			atconnect.REQGET, params={'subdomain': value},
			sendtoken=True
		)

	@property
	def motd(self) -> str:
		return self._info['motd']

	@motd.setter
	def motd(self, value:str) -> None:
		self.atserver_request(
			'https://aternos.org/panel/ajax/options/motd.php',
			atconnect.REQPOST, data={'motd': value},
			sendtoken=True
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
		return int(soft_type)

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
		return self._ram

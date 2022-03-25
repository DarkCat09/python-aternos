import enum
import json
from requests import Response
from typing import Optional

from .atconnect import AternosConnect
from .aterrors import ServerError
from .atfm import FileManager
from .atconf import AternosConfig
from .atplayers import PlayersList
from .atwss import AternosWss

class Edition(enum.IntEnum):
	java = 0
	bedrock = 1

class Status(enum.IntEnum):
	off = 0
	on = 1
	loading = 2
	shutdown = 3
	unknown = 6
	error = 7
	confirm = 10

class AternosServer:

	def __init__(
		self, servid:str,
		atconn:AternosConnect) -> None:

		self.servid = servid
		self.atconn = atconn
	
	def fetch(self) -> None:

		servreq = self.atserver_request(
			'https://aternos.org/panel/ajax/status.php',
			'GET', sendtoken=True
		)
		self._info = json.loads(servreq.content)

	def wss(self, autoconfirm:bool=False) -> AternosWss:

		return AternosWss(self, autoconfirm)

	def start(self, headstart:bool=False, accepteula:bool=True) -> None:

		startreq = self.atserver_request(
			'https://aternos.org/panel/ajax/start.php',
			'GET', params={'headstart': int(headstart)},
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
			raise ServerError(
				'EULA was not accepted. Use start(accepteula=True)'
			)

		elif error == 'already':
			raise ServerError(
				'Server is already running'
			)

		elif error == 'wrongversion':
			raise ServerError(
				'Incorrect software version installed'
			)

		elif error == 'file':
			raise ServerError(
				'File server is unavailbale, view https://status.aternos.gmbh'
			)

		elif error == 'size':
			raise ServerError(
				f'Available storage size is 4GB, ' + \
				f'your server used: {startresult["size"]}'
			)

		else:
			raise ServerError(
				f'Unable to start server, code: {error}'
			)

	def confirm(self) -> None:

		self.atserver_request(
			'https://aternos.org/panel/ajax/confirm.php',
			'GET', sendtoken=True
		)

	def stop(self) -> None:

		self.atserver_request(
			'https://aternos.org/panel/ajax/stop.php',
			'GET', sendtoken=True
		)

	def cancel(self) -> None:

		self.atserver_request(
			'https://aternos.org/panel/ajax/cancel.php',
			'GET', sendtoken=True
		)

	def restart(self) -> None:

		self.atserver_request(
			'https://aternos.org/panel/ajax/restart.php',
			'GET', sendtoken=True
		)

	def eula(self) -> None:

		self.atserver_request(
			'https://aternos.org/panel/ajax/eula.php',
			'GET', sendtoken=True
		)

	def files(self) -> FileManager:

		return FileManager(self)

	def config(self) -> AternosConfig:

		return AternosConfig(self)

	def players(self, lst:str) -> PlayersList:

		return PlayersList(lst, self)

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
			'GET', params={'subdomain': value},
			sendtoken=True
		)

	@property
	def motd(self) -> str:
		return self._info['motd']

	@motd.setter
	def motd(self, value:str) -> None:
		self.atserver_request(
			'https://aternos.org/panel/ajax/options/motd.php',
			'POST', data={'motd': value},
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
	def status(self) -> str:
		return self._info['class']

	@property
	def status_num(self) -> int:
		return int(self._info['status'])

	@property
	def ram(self) -> int:
		return int(self._info['ram'])

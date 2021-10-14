import re
import json
import lxml.html
from requests import Response
from typing import Optional, Dict

from . import atconnect
from . import aterrors
from . import atfm

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
				servtree.head.text
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
	def info(self) -> dict:
		return self._info

	@property
	def address(self) -> str:
		return f'{self.domain}:{self.port}'
	
	@property
	def domain(self) -> str:
		return self._info['displayAddress']

	@property
	def port(self) -> int:
		return self._info['port']

	@property
	def software(self) -> str:
		return self._info['software']
	
	@property
	def version(self) -> str:
		return self._info['version']

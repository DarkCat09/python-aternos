import enum
import json
import asyncio
import logging
import websockets
from typing import Union, Any, Dict, Callable, Coroutine
from typing import TYPE_CHECKING

from .atconnect import REQUA
if TYPE_CHECKING:
	from .atserver import AternosServer

class Streams(enum.Enum):

	status = (0,None)
	queue = (1,None)
	console = (2,'console')
	ram = (3,'heap')
	tps = (4,'tick')

	def __init__(self, num:int, stream:str):
		self.num = num
		self.stream = stream

class AternosWss:

	def __init__(self, atserv:'AternosServer', autoconfirm:bool=False) -> None:
		
		self.atserv = atserv
		self.cookies = atserv.atconn.session.cookies
		self.session = self.cookies['ATERNOS_SESSION']
		self.servid = atserv.servid
		self.recv = {}
		self.autoconfirm = autoconfirm
		self.confirmed = False
	
	async def confirm(self) -> None:

		self.atserv.confirm()

	def wssreceiver(self, stream:Streams) -> Callable[[Callable[[Any],Coroutine[Any,Any,None]]],Any]:
		def decorator(func:Callable[[Any],Coroutine[Any,Any,None]]) -> None:
			self.recv[stream] = func
		return decorator

	async def connect(self) -> None:
		
		headers = [
			('Host', 'aternos.org'),
			('User-Agent', REQUA),
			(
				'Cookie',
				f'ATERNOS_SESSION={self.session}; ' + \
				f'ATERNOS_SERVER={self.servid}'
			)
		]
		self.socket = await websockets.connect(
			'wss://aternos.org/hermes/',
			origin='https://aternos.org',
			extra_headers=headers
		)

		@self.wssreceiver(Streams.status)
		async def confirmfunc(msg):
			# Autoconfirm
			if not self.autoconfirm:
				return
			if msg['class'] == 'queueing' \
			and msg['queue']['pending'] == 'pending'\
			and not self.confirmed:
				self.confirm()
		
		@self.wssreceiver(Streams.status)
		async def streamsfunc(msg):
			if msg['status'] == 2:
				# Automatically start streams
				for strm in self.recv:
					if not isinstance(strm,Streams):
						continue
					if strm.stream:
						logging.debug(f'Enabling {strm.stream} stream')
						await self.send({
							'stream': strm.stream,
							'type': 'start'
						})
		
		await self.wssworker()

	async def close(self) -> None:
		
		await self.socket.close()
		del self.socket

	async def send(self, obj:Union[Dict[str, Any],str]) -> None:

		if isinstance(obj, dict):
			obj = json.dumps(obj)

		await self.socket.send(obj)

	async def wssworker(self) -> None:

		keep = asyncio.create_task(self.keepalive())
		msgs = asyncio.create_task(self.receiver())
		await keep
		await msgs

	async def keepalive(self) -> None:

		while True:
			await asyncio.sleep(49)
			await self.socket.send('{"type":"\u2764"}')

	async def receiver(self) -> None:

		while True:
			data = await self.socket.recv()
			obj = json.loads(data)
			msgtype = -1
			
			if obj['type'] == 'line':
				msgtype = Streams.console
				msg = obj['data'].strip('\r\n ')

			elif obj['type'] == 'heap':
				msgtype = Streams.ram
				msg = int(obj['data']['usage'])

			elif obj['type'] == 'tick':
				msgtype = Streams.tps
				ticks = 1000 / obj['data']['averageTickTime']
				msg = 20 if ticks > 20 else ticks

			elif obj['type'] == 'status':
				msgtype = Streams.status
				msg = json.loads(obj['message'])

			if msgtype in self.recv:
				t = asyncio.create_task(
					self.recv[msgtype](msg)
				)
				await t

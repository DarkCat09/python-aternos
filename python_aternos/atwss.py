import enum
import json
import asyncio
import websockets
from typing import Union, Any, Dict, Callable, Coroutine

from .atconnect import REQUA

class Streams(enum.IntEnum):
	status = 0
	queue = 1
	console = 2
	ram = 3
	tps = 4

class AternosWss:

	def __init__(self, session:str, servid:str) -> None:
		
		self.session = session
		self.servid = servid
		self.recv = {}

	def wssreceiver(self, stream:int) -> Callable[[Callable[[Any],Coroutine[Any,Any,None]]],Any]:
		def decorator(func:Callable[[Any],Coroutine[Any,Any,None]]) -> None:
			self.recv[stream] = func
		return decorator

	async def connect(self) -> None:
		
		headers = [
			('User-Agent', REQUA),
			(
				'Cookie',
				f'ATERNOS_SESSION={self.session}; ' +\
				f'ATERNOS_SERVER={self.servid}'
			)
		]
		self.socket = await websockets.connect(
			'wss://aternos.org/hermes',
			extra_headers=headers
		)
		asyncio.run(wssworker())

	async def close(self) -> None:
		
		await self.socket.close()
		del self.socket

	async def send(self, obj:Union[Dict[str, Any],str]) -> None:

		if isinstance(obj, dict):
			obj = json.dumps(obj)

		self.socket.send(obj)

	async def wssworker(self) -> None:

		keep = asyncio.create_task(keepalive())
		msgs = asyncio.create_task(receiver())
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

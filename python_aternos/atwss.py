"""Connects to Aternos WebSocket API
for real-time information"""

import enum
import json
import asyncio

from typing import Iterable
from typing import Union, Any
from typing import Tuple, List, Dict
from typing import Callable, Coroutine
from typing import TYPE_CHECKING

import websockets

from .atlog import log
from .atconnect import REQUA

if TYPE_CHECKING:
    from .atserver import AternosServer


OneArgT = Callable[[Any], Coroutine[Any, Any, None]]
TwoArgT = Callable[[Any, Tuple[Any, ...]], Coroutine[Any, Any, None]]
FunctionT = Union[OneArgT, TwoArgT]  # pylint: disable=invalid-name
ArgsTuple = Tuple[FunctionT, Tuple[Any, ...]]


class Streams(enum.Enum):

    """WebSocket streams types"""

    status = (0, None)
    queue = (1, None)
    console = (2, 'console')
    ram = (3, 'heap')
    tps = (4, 'tick')
    none = (-1, None)

    def __init__(self, num: int, stream: str) -> None:

        self.num = num
        self.stream = stream


class AternosWss:

    """Class for managing websocket connection"""

    def __init__(
            self,
            atserv: 'AternosServer',
            autoconfirm: bool = False) -> None:
        """Class for managing websocket connection

        Args:
            atserv (AternosServer):
                atserver.AternosServer instance
            autoconfirm (bool, optional):
                Automatically start server status listener
                when AternosWss connects to API to confirm
                server launching
        """

        self.atserv = atserv
        self.servid = atserv.servid

        cookies = atserv.atconn.session.cookies
        self.session = cookies['ATERNOS_SESSION']

        self.recv: Dict[Streams, List[ArgsTuple]]
        self.recv = {
            Streams.status: [],
            Streams.queue: [],
            Streams.console: [],
            Streams.ram: [],
            Streams.tps: [],
        }

        self.autoconfirm = autoconfirm
        self.confirmed = False

        self.socket: Any = None
        self.keep: asyncio.Task
        self.msgs: asyncio.Task

    async def confirm(self) -> None:

        """Simple way to call
        `AternosServer.confirm`
        from this class"""

        self.atserv.confirm()

    def wssreceiver(
            self,
            stream: Streams,
            arg: Tuple[Any, ...] = ()) -> Callable[[FunctionT], Any]:
        """Decorator that marks your function as a stream receiver.
        When websocket receives message from the specified stream,
        it calls all listeners created with this decorator.

        Args:
            stream (Streams): Stream that your function should listen
            arg (Tuple[Any, ...], optional): Arguments which will be passed to your function

        Returns:
            ...
        """

        def decorator(func: FunctionT) -> Callable[[Any, Any], Coroutine[Any, Any, Any]]:

            handlers = self.recv.get(stream, None)

            if handlers is None:
                self.recv[stream] = [(func, arg)]
            else:
                handlers.append((func, arg))

            async def wrapper(*args, **kwargs) -> Any:
                return await func(*args, **kwargs)

            return wrapper

        return decorator

    async def connect(self) -> None:

        """Connects to the websocket server
        and starts all stream listeners"""

        headers = [
            ('Host', 'aternos.org'),
            ('User-Agent', REQUA),
            (
                'Cookie',
                f'ATERNOS_SESSION={self.session}; '
                f'ATERNOS_SERVER={self.servid}'
            )
        ]
        self.socket = await websockets.connect(  # type: ignore
            'wss://aternos.org/hermes/',
            origin='https://aternos.org',
            extra_headers=headers
        )

        @self.wssreceiver(Streams.status)
        async def confirmfunc(msg: Dict[str, Any]) -> None:

            """Automatically confirm
            Minecraft server launching

            Args:
                msg (Dict[str, Any]): Server info dictionary
            """

            if not self.autoconfirm:
                return

            in_queue = msg['class'] == 'queueing'
            pending = msg['queue']['pending'] == 'pending'
            confirmation = in_queue and pending

            if confirmation and not self.confirmed:
                await self.confirm()

        @self.wssreceiver(Streams.status)
        async def streamsfunc(msg: Dict[str, Any]) -> None:

            """Automatically starts streams. Detailed description:

            https://github.com/DarkCat09/python-aternos/issues/22#issuecomment-1146788496
            According to the websocket messages from the web site,
            Aternos can't receive any data from a stream (e.g. console) until
            it requests this stream via the special message
            to the websocket server: `{"stream":"console","type":"start"}`
            on which the server responses with: `{"type":"connected"}`
            Also, there are RAM (used heap) and TPS (ticks per second)
            streams that must be enabled before trying to get information.
            Enabling the stream for listening the server status is not needed,
            these data is sent from API by default, so there's None value in
            the second item of its stream type tuple
            (`<Streams.status: (0, None)>`).

            Args:
                msg (Dict[str, Any]): Server info dictionary
            """

            if msg['status'] == 2:
                # Automatically start streams
                for strm in self.recv:

                    if not isinstance(strm, Streams):
                        continue

                    # If the handlers list is empty
                    if not self.recv.get(strm):
                        continue

                    if strm.stream:
                        log.debug('Requesting %s stream', strm.stream)
                        await self.send({
                            'stream': strm.stream,
                            'type': 'start'
                        })

        await self.wssworker()

    async def close(self) -> None:

        """Closes websocket connection and stops all listeners"""

        self.keep.cancel()
        self.msgs.cancel()
        await self.socket.close()
        del self.socket

    async def send(self, obj: Union[Dict[str, Any], str]) -> None:

        """Sends a message to websocket server

        Args:
            obj (Union[Dict[str, Any],str]):
                Message, may be a string or a dict
        """

        if self.socket is None:
            log.warning('Did you forget to call socket.connect?')
            await self.connect()

        assert self.socket is not None

        if isinstance(obj, dict):
            obj = json.dumps(obj)

        await self.socket.send(obj)

    async def command(self, cmd: str) -> None:

        """Sends a Minecraft command
        to the websocket server

        Args:
            cmd (str): Command, slash at
                the beginning is not required
        """

        await self.send(
            {
                'stream': 'console',
                'type': 'command',
                'data': cmd,
            }
        )

    async def wssworker(self) -> None:

        """Starts async tasks in background
        for receiving websocket messages
        and sending keepalive ping"""

        self.keep = asyncio.create_task(self.keepalive())
        self.msgs = asyncio.create_task(self.receiver())

    async def keepalive(self) -> None:

        """Each 49 seconds sends keepalive ping
        to the websocket server"""

        try:
            while True:
                await asyncio.sleep(49)
                await self.socket.send('{"type":"\u2764"}')

        except asyncio.CancelledError:
            pass

    async def receiver(self) -> None:

        """Receives messages from websocket servers
        and calls user's streams listeners"""

        while True:
            try:
                data = await self.socket.recv()
                obj = json.loads(data)
                msgtype = Streams.none

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

                    # function info tuples
                    handlers: Iterable[ArgsTuple]
                    handlers = self.recv.get(msgtype, ())

                    for func in handlers:

                        # if arguments is not empty
                        if func[1]:
                            # call the function with args
                            coro = func[0](msg, func[1])  # type: ignore

                        else:
                            # mypy error: too few arguments
                            # looks like a bug, so it is ignored
                            coro = func[0](msg)  # type: ignore

                        # run
                        asyncio.create_task(coro)

            except asyncio.CancelledError:
                break

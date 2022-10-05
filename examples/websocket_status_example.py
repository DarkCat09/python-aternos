import asyncio
import logging
from getpass import getpass

from typing import Tuple, Dict, Any

from python_aternos import Client, Streams

# Request credentials
user = input('Username: ')
pswd = getpass('Password: ')

# Debug logging
logs = input('Show detailed logs? (y/n) ').strip().lower() == 'y'
if logs:
    logging.basicConfig(level=logging.DEBUG)

# Authentication
aternos = Client.from_credentials(user, pswd)

server = aternos.list_servers()[0]
socket = server.wss()


# Handler for server status
@socket.wssreceiver(Streams.status, ('Server 1',))
async def state(
        msg: Dict[Any, Any],
        args: Tuple[str]) -> None:

    print(args[0], 'received', len(msg), 'symbols')

    server._info = msg
    print(
        args[0],
        server.subdomain,
        'is',
        server.status
    )


# Main function
async def main() -> None:
    server.start()
    await socket.connect()
    await asyncio.create_task(loop())


# Keepalive
async def loop() -> None:
    while True:
        await asyncio.Future()


asyncio.run(main())

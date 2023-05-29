import asyncio
from getpass import getpass

from typing import Tuple, Dict, Any

from python_aternos import Client, Streams


# Request credentials
user = input('Username: ')
pswd = getpass('Password: ')

# Instantiate Client
atclient = Client()
aternos = atclient.account

# Enable debug logging
logs = input('Show detailed logs? (y/n) ').strip().lower() == 'y'
if logs:
    atclient.debug = True

# Authenticate
atclient.login(user, pswd)

server = aternos.list_servers()[0]
socket = server.wss()


# Handler for console messages
@socket.wssreceiver(Streams.console, ('Server 1',))  # type: ignore
async def console(
        msg: Dict[Any, Any],
        args: Tuple[str]) -> None:

    print(args[0], 'received', msg)


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

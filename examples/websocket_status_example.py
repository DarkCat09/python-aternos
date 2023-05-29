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


# Handler for server status
@socket.wssreceiver(Streams.status, ('Server 1',))  # type: ignore
async def state(
        msg: Dict[Any, Any],
        args: Tuple[str]) -> None:

    # For debugging
    print(args[0], 'received', len(msg), 'symbols')

    # Write new info dictionary
    server._info = msg

    # Server 1 test is online
    print(
        args[0],
        server.subdomain,
        'is',
        server.status
    )

    # Server 1 players: ['DarkCat09', 'someone']
    print(
        args[0],
        'players:',
        server.players_list
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

import asyncio
import logging
from getpass import getpass
from python_aternos import Client, atwss

user = input('Username: ')
pswd = getpass('Password: ')

logs = input('Show detailed logs? (y/n) ').strip().lower() == 'y'
if logs:
    logging.basicConfig(level=logging.DEBUG)

aternos = Client.from_credentials(user, pswd)

s = aternos.list_servers()[0]
socket = s.wss()


@socket.wssreceiver(atwss.Streams.console, 'Server 1')
async def console(msg, args):
    print(args[0], 'received', msg)


async def main():
    s.start()
    await socket.connect()
    await asyncio.create_task(loop())


async def loop():
    while True:
        await asyncio.sleep(1)

asyncio.run(main())

import asyncio
from getpass import getpass
from python_aternos import Client, atwss

user = input('Username: ')
pswd = getpass('Password: ')
aternos = Client.from_credentials(user, pswd)

s = aternos.list_servers()[0]
socket = s.wss()


@socket.wssreceiver(atwss.Streams.console)
async def console(msg):
    print('Received:', msg)


async def main():
    s.start()
    await socket.connect()
    await asyncio.create_task(loop())


async def loop():
    while True:
        await asyncio.sleep(1)

asyncio.run(main())

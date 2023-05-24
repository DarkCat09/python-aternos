import asyncio
import aioconsole
from getpass import getpass
from python_aternos import Client, atwss

user = input('Username: ')
pswd = getpass('Password: ')
resp = input('Show responses? ').upper() == 'Y'

atclient = Client()
aternos = atclient.account
atclient.login(user, pswd)

s = aternos.list_servers()[0]
socket = s.wss()

if resp:
    @socket.wssreceiver(atwss.Streams.console)
    async def console(msg):
        print('<', msg)


async def main():
    s.start()
    await asyncio.gather(
        socket.connect(),
        commands()
    )


async def commands():
    while True:
        cmd = await aioconsole.ainput('> ')
        if cmd.strip() == '':
            continue
        await socket.send({
            'stream': 'console',
            'type': 'command',
            'data': cmd
        })

asyncio.run(main())

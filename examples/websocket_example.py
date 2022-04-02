from getpass import getpass
from python_aternos import Client, atwss

user = input('Username: ')
pswd = getpass('Password: ')
aternos = Client.from_credentials(user, pswd)

s = aternos.list_servers()[0]
socket = s.wss()

@socket.wssreceiver(atwss.Streams.console)
async def console(msg):
    print('Received: ' + msg)

s.start()

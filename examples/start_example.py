from getpass import getpass
from python_aternos import Client

user = input('Username: ')
pswd = getpass('Password: ')
aternos = Client.from_credentials(user, pswd)

srvs = aternos.servers
print(srvs)

s = srvs[0]
s.start()

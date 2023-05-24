from getpass import getpass
from python_aternos import Client

user = input('Username: ')
pswd = getpass('Password: ')

atclient = Client()
aternos = atclient.account
atclient.login(user, pswd)

srvs = aternos.list_servers()
print(srvs)

s = srvs[0]
s.start()

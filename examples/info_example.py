from getpass import getpass
from python_aternos import Client, atserver

user = input('Username: ')
pswd = getpass('Password: ')
aternos = Client.from_credentials(user, pswd)

srvs = aternos.list_servers()
for srv in srvs:
    print('*** ' + srv.domain + ' ***')
    print(srv.motd)
    print('*** Status:', srv.status)
    print('*** Full address:', srv.address)
    print('*** Port:', srv.port)
    print('*** Name:', srv.subdomain)
    print('*** Minecraft:', srv.software, srv.version)
    print('*** IsBedrock:', srv.edition == atserver.Edition.bedrock)
    print('*** IsJava:', srv.edition == atserver.Edition.java)

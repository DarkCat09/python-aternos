from getpass import getpass

from selenium.webdriver import Firefox
from python_aternos import Client

user = input('Username: ')
pswd = getpass('Password: ')

with Firefox() as driver:

    atclient = Client(driver)
    atclient.login(user, pswd)

    servers = atclient.list_servers()

    # for serv in servers:
    #     print(
    #         serv.id, serv.name,
    #         serv.software,
    #         serv.status,
    #         serv.players,
    #     )
    list(map(print, servers))

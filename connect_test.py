from python_aternos import Client as AternosClient

aternos = AternosClient('', password='')

srvs = aternos.servers

print(srvs)

s = srvs[0]

s.start()

import lxml.html
from typing import List

from . import atserver
from . import atconnect

class AternosPlayersList:

	def __init__(self, lst:str, atserv:atserver.AternosServer) -> None:

		self.atserv = atserv
		self.lst = lst

	def add(self, name:str) -> None:

		self.atserv.atserver_request(
			'https://aternos.org/panel/ajax/players/add.php',
			atconnect.REQPOST, data={
				'list': self.lst,
				'name': name
			}
		)

	def remove(self, name:str) -> None:

		self.atserv.atserver_request(
			'https://aternos.org/panel/ajax/players/remove.php',
			atconnect.REQPOST, data={
				'list': self.lst,
				'name': name
			}
		)

	@property
	def players(self) -> List[str]:
		listreq = atserv.atserver_request(
			f'https://aternos.org/players/{lst}',
			atconnect.REQGET
		)
		listtree = lxml.html.fromstring(listreq.content)

		items = listtree.xpath(
			'//div[@class="player-list"]' + \
			'/div[@class="list-item-container"]' + \
			'/div[@class="list-item"]'
		)
		result = []
		for i in items:
			name = i.xpath('./div[@class="list-name"]')
			result.append(name)

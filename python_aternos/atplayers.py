import enum
import lxml.html
from typing import List
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from .atserver import AternosServer

class Lists(enum.Enum):

	whl = 'whitelist'
	ops = 'ops'
	ban = 'banned-players'
	ips = 'banned-ips'

class PlayersList:

	def __init__(self, lst:str, atserv:'AternosServer') -> None:

		for ltype in Lists:
			if ltype.value == lst:
				break
		else:
			raise ValueError(
				'Incorrect players list type! ' + \
				'Use atplayers.Lists enum'
			)
		
		self.atserv = atserv
		self.lst = lst
		self.players = []

	def list_players(self, cache:bool=True) -> List[str]:

		if cache:
			return self.players

		listreq = self.atserv.atserver_request(
			f'https://aternos.org/players/{self.lst}', 'GET'
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
		return result

	def add(self, name:str) -> None:

		self.atserv.atserver_request(
			'https://aternos.org/panel/ajax/players/add.php',
			'POST', data={
				'list': self.lst,
				'name': name
			}
		)

		self.players.append(name)

	def remove(self, name:str) -> None:

		self.atserv.atserver_request(
			'https://aternos.org/panel/ajax/players/remove.php',
			'POST', data={
				'list': self.lst,
				'name': name
			}
		)

		for i, j in enumerate(self.players):
			if j == name:
				del self.players[i]

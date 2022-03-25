import enum
import lxml.html
from typing import List, Union
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from .atserver import AternosServer

class Lists(enum.Enum):

	whl = 'whitelist'
	ops = 'ops'
	ban = 'banned-players'
	ips = 'banned-ips'

class PlayersList:

	def __init__(self, lst:Union[str,Lists], atserv:'AternosServer') -> None:

		self.atserv = atserv
		self.lst = Lists(lst)
		self.players = []
		self.parsed = False

	def list_players(self, cache:bool=True) -> List[str]:

		if cache and self.parsed:
			return self.players

		listreq = self.atserv.atserver_request(
			f'https://aternos.org/players/{self.lst.value}',
			'GET'
		)
		listtree = lxml.html.fromstring(listreq.content)
		items = listtree.xpath(
			'//div[@class="list-item"]'
		)

		result = []
		for i in items:
			name = i.xpath('./div[@class="list-name"]')
			result.append(name[0].text.strip())
		
		self.players = result
		self.parsed = True
		return result

	def add(self, name:str) -> None:

		self.atserv.atserver_request(
			'https://aternos.org/panel/ajax/players/add.php',
			'POST', data={
				'list': self.lst.value,
				'name': name
			}, sendtoken=True
		)

		self.players.append(name)

	def remove(self, name:str) -> None:

		self.atserv.atserver_request(
			'https://aternos.org/panel/ajax/players/remove.php',
			'POST', data={
				'list': self.lst.value,
				'name': name
			}, sendtoken=True
		)

		for i, j in enumerate(self.players):
			if j == name:
				del self.players[i]

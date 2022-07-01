import enum
import lxml.html
from typing import List, Union
from typing import TYPE_CHECKING

from .atserver import Edition
if TYPE_CHECKING:
    from .atserver import AternosServer


class Lists(enum.Enum):

    """Players list type enum"""

    whl = 'whitelist'
    whl_je = 'whitelist'
    whl_be = 'allowlist'
    ops = 'ops'
    ban = 'banned-players'
    ips = 'banned-ips'


class PlayersList:

    """Class for managing operators, whitelist and banned players lists

    :param lst: Players list type, must be
    :class:`python_aternos.atplayers.Lists` enum value
    :type lst: Union[str,Lists]
    :param atserv: :class:`python_aternos.atserver.AternosServer` instance
    :type atserv: python_aternos.atserver.AternosServer
    """

    def __init__(self, lst: Union[str, Lists], atserv: 'AternosServer') -> None:

        self.atserv = atserv
        self.lst = Lists(lst)

        common_whl = (self.lst == Lists.whl)
        bedrock = (atserv.edition == Edition.bedrock)
        if common_whl and bedrock:
            self.lst = Lists.whl_be

        self.players: List[str] = []
        self.parsed = False

    def list_players(self, cache: bool = True) -> List[str]:

        """Parse a players list

        :param cache: If the function can return
        cached list (highly recommended), defaults to True
        :type cache: bool, optional
        :return: List of players nicknames
        :rtype: List[str]
        """

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

    def add(self, name: str) -> None:

        """Appends a player to the list by the nickname

        :param name: Player's nickname
        :type name: str
        """

        self.atserv.atserver_request(
            'https://aternos.org/panel/ajax/players/add.php',
            'POST', data={
                'list': self.lst.value,
                'name': name
            }, sendtoken=True
        )

        self.players.append(name)

    def remove(self, name: str) -> None:

        """Removes a player from the list by the nickname

        :param name: Player's nickname
        :type name: str
        """

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

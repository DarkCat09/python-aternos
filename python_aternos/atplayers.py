"""Operators, whitelist and banned players lists"""

import enum

from typing import List, Union
from typing import TYPE_CHECKING

import lxml.html

from .atconnect import BASE_URL, AJAX_URL
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

    """Class for managing operators,
    whitelist and banned players lists"""

    def __init__(
            self,
            lst: Union[str, Lists],
            atserv: 'AternosServer') -> None:
        """Class for managing operators,
        whitelist and banned players lists

        Args:
            lst (Union[str,Lists]): Players list type, must be
                atplayers.Lists enum value
            atserv (python_aternos.atserver.AternosServer):
                atserver.AternosServer instance
        """

        self.atserv = atserv
        self.lst = Lists(lst)

        # Fix for #30 issue
        # whl_je = whitelist for java
        # whl_be = whitelist for bedrock
        # whl = common whitelist
        common_whl = self.lst == Lists.whl
        bedrock = atserv.is_bedrock

        if common_whl and bedrock:
            self.lst = Lists.whl_be

        self.players: List[str] = []
        self.parsed = False

    def list_players(self, cache: bool = True) -> List[str]:
        """Parse a players list

        Args:
            cache (bool, optional): If the function should
                return cached list (highly recommended)

        Returns:
            List of players' nicknames
        """

        if cache and self.parsed:
            return self.players

        listreq = self.atserv.atserver_request(
            f'{BASE_URL}/players/{self.lst.value}',
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

        Args:
            name (str): Player's nickname
        """

        self.atserv.atserver_request(
            f'{AJAX_URL}/server/players/lists/add',
            'POST', data={
                'list': self.lst.value,
                'name': name
            }, sendtoken=True
        )

        self.players.append(name)

    def remove(self, name: str) -> None:
        """Removes a player from the list by the nickname

        Args:
            name (str): Player's nickname
        """

        self.atserv.atserver_request(
            f'{AJAX_URL}/server/players/lists/remove',
            'POST', data={
                'list': self.lst.value,
                'name': name
            }, sendtoken=True
        )

        for i, j in enumerate(self.players):
            if j == name:
                del self.players[i]

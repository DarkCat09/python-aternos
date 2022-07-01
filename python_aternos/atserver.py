"""Aternos Minecraft server"""

import enum
import json
from requests import Response
from typing import Optional, List

from .atconnect import AternosConnect
from .aterrors import ServerStartError
from .atfm import FileManager
from .atconf import AternosConfig
from .atplayers import PlayersList
from .atplayers import Lists
from .atwss import AternosWss


class Edition(enum.IntEnum):

    """Server edition type enum"""

    java = 0
    bedrock = 1


class Status(enum.IntEnum):

    """Server numeric status enum.
    It is highly recommended to use
    `AternosServer.status` instead of
    `AternosServer.status_num`"""

    off = 0
    on = 1
    starting = 2
    shutdown = 3
    unknown = 6
    error = 7
    confirm = 10


class AternosServer:

    """Class for controlling your Aternos Minecraft server

    :param servid: Unique server IDentifier
    :type servid: str
    :param atconn: :class:`python_aternos.atconnect.AternosConnect`
    instance with initialized Aternos session
    :type atconn: python_aternos.atconnect.AternosConnect
    :param reqinfo: Automatically call AternosServer.fetch()
    to get all info, defaults to `True`
    :type reqinfo: bool, optional
    """

    def __init__(
            self, servid: str,
            atconn: AternosConnect,
            reqinfo: bool = True) -> None:

        self.servid = servid
        self.atconn = atconn
        if reqinfo:
            self.fetch()

    def fetch(self) -> None:

        """Send a request to Aternos API to get all server info"""

        servreq = self.atserver_request(
            'https://aternos.org/panel/ajax/status.php',
            'GET', sendtoken=True
        )
        self._info = json.loads(servreq.content)

    def wss(self, autoconfirm: bool = False) -> AternosWss:

        """Returns :class:`python_aternos.atwss.AternosWss`
        instance for listening server streams in real-time

        :param autoconfirm: Automatically start server status listener
        when AternosWss connects to API to confirm
        server launching, defaults to `False`
        :type autoconfirm: bool, optional
        :return: :class:`python_aternos.atwss.AternosWss` object
        :rtype: python_aternos.atwss.AternosWss
        """

        return AternosWss(self, autoconfirm)

    def start(
            self,
            headstart: bool = False,
            accepteula: bool = True) -> None:

        """Starts a server

        :param headstart: Start a server in the headstart mode
        which allows you to skip all queue, defaults to `False`
        :type headstart: bool, optional
        :param accepteula: Automatically accept
        the Mojang EULA, defaults to `True`
        :type accepteula: bool, optional
        :raises ServerStartError: When Aternos
        is unable to start the server
        """

        startreq = self.atserver_request(
            'https://aternos.org/panel/ajax/start.php',
            'GET', params={'headstart': int(headstart)},
            sendtoken=True
        )
        startresult = startreq.json()

        if startresult['success']:
            return

        error = startresult['error']

        if error == 'eula' and accepteula:
            self.eula()
            self.start(accepteula=False)
            return

        raise ServerStartError(error)

    def confirm(self) -> None:

        """Confirms server launching"""

        self.atserver_request(
            'https://aternos.org/panel/ajax/confirm.php',
            'GET', sendtoken=True
        )

    def stop(self) -> None:

        """Stops the server"""

        self.atserver_request(
            'https://aternos.org/panel/ajax/stop.php',
            'GET', sendtoken=True
        )

    def cancel(self) -> None:

        """Cancels server launching"""

        self.atserver_request(
            'https://aternos.org/panel/ajax/cancel.php',
            'GET', sendtoken=True
        )

    def restart(self) -> None:

        """Restarts the server"""

        self.atserver_request(
            'https://aternos.org/panel/ajax/restart.php',
            'GET', sendtoken=True
        )

    def eula(self) -> None:

        """Accepts the Mojang EULA"""

        self.atserver_request(
            'https://aternos.org/panel/ajax/eula.php',
            'GET', sendtoken=True
        )

    def files(self) -> FileManager:

        """Returns :class:`python_aternos.atfm.FileManager`
        instance for file operations

        :return: :class:`python_aternos.atfm.FileManager` object
        :rtype: python_aternos.atfm.FileManager
        """

        return FileManager(self)

    def config(self) -> AternosConfig:

        """Returns :class:`python_aternos.atconf.AternosConfig`
        instance for editing server settings

        :return: :class:`python_aternos.atconf.AternosConfig` object
        :rtype: python_aternos.atconf.AternosConfig
        """

        return AternosConfig(self)

    def players(self, lst: Lists) -> PlayersList:

        """Returns :class:`python_aternos.atplayers.PlayersList`
        instance for managing operators, whitelist and banned players lists

        :param lst: Players list type, must be
        the :class:`python_aternos.atplayers.Lists` enum value
        :type lst: python_aternos.atplayers.Lists
        :return: :class:`python_aternos.atplayers.PlayersList`
        :rtype: python_aternos.atplayers.PlayersList
        """

        return PlayersList(lst, self)

    def atserver_request(
            self, url: str, method: str,
            params: Optional[dict] = None,
            data: Optional[dict] = None,
            headers: Optional[dict] = None,
            sendtoken: bool = False) -> Response:

        """Sends a request to Aternos API
        with server IDenitfier parameter

        :param url: Request URL
        :type url: str
        :param method: Request method, must be GET or POST
        :type method: str
        :param params: URL parameters, defaults to None
        :type params: Optional[dict], optional
        :param data: POST request data, if the method is GET,
        this dict will be combined with params, defaults to None
        :type data: Optional[dict], optional
        :param headers: Custom headers, defaults to None
        :type headers: Optional[dict], optional
        :param sendtoken: If the ajax and SEC token
        should be sent, defaults to False
        :type sendtoken: bool, optional
        :return: API response
        :rtype: requests.Response
        """

        return self.atconn.request_cloudflare(
            url=url, method=method,
            params=params, data=data,
            headers=headers,
            reqcookies={
                'ATERNOS_SERVER': self.servid
            },
            sendtoken=sendtoken
        )

    @property
    def subdomain(self) -> str:

        """Server subdomain (part of domain before `.aternos.me`)

        :return: Subdomain
        :rtype: str
        """

        atdomain = self.domain
        return atdomain[:atdomain.find('.')]

    @subdomain.setter
    def subdomain(self, value: str) -> None:

        """Set new subdomain for your server

        :param value: Subdomain
        :type value: str
        """

        self.atserver_request(
            'https://aternos.org/panel/ajax/options/subdomain.php',
            'GET', params={'subdomain': value},
            sendtoken=True
        )

    @property
    def motd(self) -> str:

        """Server message of the day,
        which is shown below its name in the servers list

        :return: MOTD
        :rtype: str
        """

        return self._info['motd']

    @motd.setter
    def motd(self, value: str) -> None:

        """Set new message of the day

        :param value: MOTD
        :type value: str
        """

        self.atserver_request(
            'https://aternos.org/panel/ajax/options/motd.php',
            'POST', data={'motd': value},
            sendtoken=True
        )

    @property
    def address(self) -> str:

        """Full server address including domain and port

        :return: Server address
        :rtype: str
        """

        return self._info['displayAddress']

    @property
    def domain(self) -> str:

        """Server domain (test.aternos.me),
        address without port number

        :return: Domain
        :rtype: str
        """

        return self._info['ip']

    @property
    def port(self) -> int:

        """Server port number

        :return: Port
        :rtype: int
        """

        return self._info['port']

    @property
    def edition(self) -> Edition:

        """Server software edition: Java or Bedrock

        :return: Software edition
        :rtype: Edition
        """

        soft_type = self._info['bedrock']
        return Edition(soft_type)

    @property
    def software(self) -> str:

        """Server software name (e.g. `Vanilla`)

        :return: Software name
        :rtype: str
        """

        return self._info['software']

    @property
    def version(self) -> str:

        """Server software version (e.g. `1.16.5`)

        :return: Software version
        :rtype: str
        """

        return self._info['version']

    @property
    def status(self) -> str:

        """Server status string (offline, loading)

        :return: Status string
        :rtype: str
        """

        return self._info['class']

    @property
    def status_num(self) -> int:

        """Server numeric status. It is highly recommended
        to use status string instead of a number.

        :return: Status code
        :rtype: Status
        """

        return Status(self._info['status'])

    @property
    def players_list(self) -> List[str]:

        """List of connected players nicknames

        :return: Connected players
        :rtype: List[str]
        """

        return self._info['playerlist']

    @property
    def players_count(self) -> int:

        """How many connected players

        :return: Connected players count
        :rtype: int
        """

        return int(self._info['players'])

    @property
    def slots(self) -> int:

        """Server slots, how many players can connect

        :return: Slots count
        :rtype: int
        """

        return int(self._info['slots'])

    @property
    def ram(self) -> int:

        """Server used RAM in MB

        :return: Used RAM
        :rtype: int
        """

        return int(self._info['ram'])

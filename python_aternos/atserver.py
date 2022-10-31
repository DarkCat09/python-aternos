"""Aternos Minecraft server"""

import enum
import json

from typing import Optional
from typing import List, Dict, Any

import requests

from .atconnect import AternosConnect
from .aterrors import ServerStartError
from .atfm import FileManager
from .atconf import AternosConfig
from .atplayers import PlayersList
from .atplayers import Lists
from .atwss import AternosWss


class Edition(enum.IntEnum):

    """Server edition type enum (java, bedrock)"""

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

    loading = 6
    error = 7

    preparing = 10
    confirm = 10


class AternosServer:

    """Class for controlling your Aternos Minecraft server"""

    def __init__(
            self, servid: str,
            atconn: AternosConnect,
            reqinfo: bool = True) -> None:
        """Class for controlling your Aternos Minecraft server

        Args:
            servid (str): Unique server IDentifier
            atconn (AternosConnect):
                AternosConnect instance with initialized Aternos session
            reqinfo (bool, optional): Automatically call
                `fetch()` to get all info
        """

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
        """Returns AternosWss instance for
        listening server streams in real-time

        Args:
            autoconfirm (bool, optional):
                Automatically start server status listener
                when AternosWss connects to API to confirm
                server launching

        Returns:
            AternosWss object
        """

        return AternosWss(self, autoconfirm)

    def start(
            self,
            headstart: bool = False,
            accepteula: bool = True) -> None:
        """Starts a server

        Args:
            headstart (bool, optional): Start a server in
                the headstart mode which allows
                you to skip all queue
            accepteula (bool, optional):
                Automatically accept the Mojang EULA

        Raises:
            ServerStartError: When Aternos
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
        """Returns FileManager instance
        for file operations

        Returns:
            FileManager object
        """

        return FileManager(self)

    def config(self) -> AternosConfig:
        """Returns AternosConfig instance
        for editing server settings

        Returns:
            AternosConfig object
        """

        return AternosConfig(self)

    def players(self, lst: Lists) -> PlayersList:
        """Returns PlayersList instance
        for managing operators, whitelist
        and banned players lists

        Args:
            lst (Lists): Players list type,
                must be the atplayers.Lists enum value

        Returns:
            PlayersList object
        """

        return PlayersList(lst, self)

    def atserver_request(
            self, url: str, method: str,
            params: Optional[Dict[Any, Any]] = None,
            data: Optional[Dict[Any, Any]] = None,
            headers: Optional[Dict[Any, Any]] = None,
            sendtoken: bool = False) -> requests.Response:
        """Sends a request to Aternos API
        with server IDenitfier parameter

        Args:
            url (str): Request URL
            method (str): Request method, must be GET or POST
            params (Optional[Dict[Any, Any]], optional): URL parameters
            data (Optional[Dict[Any, Any]], optional): POST request data,
                if the method is GET, this dict
                will be combined with params
            headers (Optional[Dict[Any, Any]], optional): Custom headers
            sendtoken (bool, optional): If the ajax and SEC token should be sent

        Returns:
            API response
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
        """Server subdomain
        (the part of domain before `.aternos.me`)

        Returns:
            Subdomain
        """

        atdomain = self.domain
        return atdomain[:atdomain.find('.')]

    @subdomain.setter
    def subdomain(self, value: str) -> None:
        """Set a new subdomain for your server

        Args:
            value (str): Subdomain
        """

        self.atserver_request(
            'https://aternos.org/panel/ajax/options/subdomain.php',
            'GET', params={'subdomain': value},
            sendtoken=True
        )

    @property
    def motd(self) -> str:
        """Server message of the day
        which is shown below its name
        in the Minecraft servers list

        Returns:
            MOTD
        """

        return self._info['motd']

    @motd.setter
    def motd(self, value: str) -> None:
        """Set a new message of the day

        Args:
            value (str): New MOTD
        """

        self.atserver_request(
            'https://aternos.org/panel/ajax/options/motd.php',
            'POST', data={'motd': value},
            sendtoken=True
        )

    @property
    def address(self) -> str:
        """Full server address
        including domain and port

        Returns:
            Server address
        """

        return self._info['displayAddress']

    @property
    def domain(self) -> str:
        """Server domain (e.g. `test.aternos.me`).
        In other words, address without port number

        Returns:
            Domain
        """

        return self._info['ip']

    @property
    def port(self) -> int:
        """Server port number

        Returns:
            Port
        """

        return self._info['port']

    @property
    def edition(self) -> Edition:
        """Server software edition: Java or Bedrock

        Returns:
            Software edition
        """

        soft_type = self._info['bedrock']
        return Edition(soft_type)

    @property
    def is_java(self) -> bool:
        """Check if server software is Java Edition

        Returns:
            Is it Minecraft JE
        """

        return not self._info['bedrock']

    @property
    def is_bedrock(self) -> bool:
        """Check if server software is Bedrock Edition

        Returns:
            Is it Minecraft BE
        """

        return bool(self._info['bedrock'])

    @property
    def software(self) -> str:
        """Server software name (e.g. `Vanilla`)

        Returns:
            Software name
        """

        return self._info['software']

    @property
    def version(self) -> str:
        """Server software version (1.16.5)

        Returns:
            Software version
        """

        return self._info['version']

    @property
    def css_class(self) -> str:
        """CSS class for
        server status block
        on official web site
        (offline, loading,
        loading starting, queueing)

        Returns:
            CSS class
        """

        return self._info['class']

    @property
    def status(self) -> str:
        """Server status string
        (offline, loading, preparing)

        Returns:
            Status string
        """

        return self._info['lang']

    @property
    def status_num(self) -> Status:
        """Server numeric status.
        It is highly recommended to use
        status string instead of a number

        Returns:
            Status code
        """

        return Status(self._info['status'])

    @property
    def players_list(self) -> List[str]:
        """List of connected players' nicknames

        Returns:
            Connected players
        """

        return self._info['playerlist']

    @property
    def players_count(self) -> int:
        """How many players are connected

        Returns:
            Connected players count
        """

        return int(self._info['players'])

    @property
    def slots(self) -> int:
        """Server slots, how many
        players **can** connect

        Returns:
            Slots count
        """

        return int(self._info['slots'])

    @property
    def ram(self) -> int:
        """Server used RAM in MB

        Returns:
            Used RAM
        """

        return int(self._info['ram'])

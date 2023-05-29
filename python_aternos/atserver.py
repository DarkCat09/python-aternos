"""Aternos Minecraft server"""

import re
import json

import enum
from typing import Any, Dict, List
from functools import partial

from .atconnect import BASE_URL, AJAX_URL
from .atconnect import AternosConnect
from .atwss import AternosWss

from .atplayers import PlayersList
from .atplayers import Lists

from .atfm import FileManager
from .atconf import AternosConfig

from .aterrors import AternosError
from .aterrors import ServerStartError


SERVER_URL = f'{AJAX_URL}/server'
status_re = re.compile(
    r'<script>\s*var lastStatus\s*?=\s*?(\{.+?\});?\s*<\/script>'
)


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
            autofetch: bool = False) -> None:
        """Class for controlling your Aternos Minecraft server

        Args:
            servid (str): Unique server IDentifier
            atconn (AternosConnect):
                AternosConnect instance with initialized Aternos session
            autofetch (bool, optional): Automatically call
                `fetch()` to get all info
        """

        self.servid = servid
        self.atconn = atconn

        self._info: Dict[str, Any] = {}

        self.atserver_request = partial(
            self.atconn.request_cloudflare,
            reqcookies={
                'ATERNOS_SERVER': self.servid,
            }
        )

        if autofetch:
            self.fetch()

    def fetch(self) -> None:
        """Get all server info"""

        page = self.atserver_request(
            f'{BASE_URL}/server', 'GET'
        )
        match = status_re.search(page.text)

        if match is None:
            raise AternosError('Unable to parse lastStatus object')

        self._info = json.loads(match[1])

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
            access_credits: bool = False,
            accepteula: bool = True) -> None:
        """Starts a server

        Args:
            headstart (bool, optional): Start a server in
                the headstart mode which allows
                you to skip all queue
            access_credits (bool, optional):
                Some new parameter in Aternos API,
                I don't know what it is
            accepteula (bool, optional):
                Automatically accept the Mojang EULA

        Raises:
            ServerStartError: When Aternos
                is unable to start the server
        """

        startreq = self.atserver_request(
            f'{SERVER_URL}/start',
            'GET', params={
                'headstart': int(headstart),
                'access-credits': int(access_credits),
            },
            sendtoken=True,
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
            f'{SERVER_URL}/confirm',
            'GET', sendtoken=True,
        )

    def stop(self) -> None:
        """Stops the server"""

        self.atserver_request(
            f'{SERVER_URL}/stop',
            'GET', sendtoken=True,
        )

    def cancel(self) -> None:
        """Cancels server launching"""

        self.atserver_request(
            f'{SERVER_URL}/cancel',
            'GET', sendtoken=True,
        )

    def restart(self) -> None:
        """Restarts the server"""

        self.atserver_request(
            f'{SERVER_URL}/restart',
            'GET', sendtoken=True,
        )

    def eula(self) -> None:
        """Sends a request to accept the Mojang EULA"""

        self.atserver_request(
            f'{SERVER_URL}/accept-eula',
            'GET', sendtoken=True,
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

    def set_subdomain(self, value: str) -> None:
        """Set a new subdomain for your server
        (the part before `.aternos.me`)

        Args:
            value (str): Subdomain
        """

        self.atserver_request(
            f'{SERVER_URL}/options/set-subdomain',
            'GET', params={'subdomain': value},
            sendtoken=True,
        )

    def set_motd(self, value: str) -> None:
        """Set new Message of the Day
        (shown below the name in the Minecraft servers list).
        Formatting with "paragraph sign + code" is supported,
        see https://minecraft.tools/color-code.php

        Args:
            value (str): MOTD
        """

        self.atserver_request(
            f'{SERVER_URL}/options/set-motd',
            'POST', data={'motd': value},
            sendtoken=True,
        )

    @property
    def subdomain(self) -> str:
        """Get the server subdomain
        (the part before `.aternos.me`)

        Returns:
            Subdomain
        """

        atdomain = self.domain
        return atdomain[:atdomain.find('.')]

    @property
    def motd(self) -> str:
        """Get the server message of the day
        (shown below its name in Minecraft servers list)

        Returns:
            MOTD
        """

        return self._info['motd']

    @property
    def address(self) -> str:
        """Full server address
        including domain and port

        Returns:
            Server address
        """

        return f'{self.domain}:{self.port}'

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
        """CSS class for the server status element
        on official web site: offline, online, loading, etc.
        See https://aternos.dc09.ru/howto/server/#server-info

        In most cases you need `AternosServer.status` instead of this

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

    @property
    def countdown(self) -> int:
        """Server stop countdown
        in seconds

        Returns:
            Stop countdown
        """

        value = self._info['countdown']
        return int(value or -1)

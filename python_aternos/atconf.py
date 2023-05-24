"""Modifying server and world options"""

# TODO: Still needs refactoring

import enum
import re

from typing import Any, Dict, List, Union, Optional
from typing import TYPE_CHECKING

import lxml.html

from .atconnect import BASE_URL, AJAX_URL
if TYPE_CHECKING:
    from .atserver import AternosServer


DAT_PREFIX = 'Data:'
DAT_GR_PREFIX = 'Data:GameRules:'


class ServerOpts(enum.Enum):

    """server.options file"""

    players = 'max-players'
    gm = 'gamemode'
    difficulty = 'difficulty'
    whl = 'white-list'
    online = 'online-mode'
    pvp = 'pvp'
    cmdblock = 'enable-command-block'
    flight = 'allow-flight'
    animals = 'spawn-animals'
    monsters = 'spawn-monsters'
    villagers = 'spawn-npcs'
    nether = 'allow-nether'
    forcegm = 'force-gamemode'
    spawnlock = 'spawn-protection'
    cmds = 'allow-cheats'
    packreq = 'require-resource-pack'
    pack = 'resource-pack'


class WorldOpts(enum.Enum):

    """level.dat file"""

    seed12 = 'randomseed'
    seed = 'seed'
    hardcore = 'hardcore'
    difficulty = 'Difficulty'


class WorldRules(enum.Enum):

    """/gamerule list"""

    advs = 'announceAdvancements'
    univanger = 'universalAnger'
    cmdout = 'commandBlockOutput'
    elytra = 'disableElytraMovementCheck'
    raids = 'disableRaids'
    daynight = 'doDaylightCycle'
    entdrop = 'doEntityDrops'
    fire = 'doFireTick'
    phantoms = 'doInsomnia'
    immrespawn = 'doImmediateRespawn'
    limitcraft = 'doLimitedCrafting'
    mobloot = 'doMobLoot'
    mobs = 'doMobSpawning'
    patrols = 'doPatrolSpawning'
    blockdrop = 'doTileDrops'
    traders = 'doTraderSpawning'
    weather = 'doWeatherCycle'
    drowndmg = 'drowningDamage'
    falldmg = 'fallDamage'
    firedmg = 'fireDamage'
    snowdmg = 'freezeDamage'
    forgive = 'forgiveDeadPlayers'
    keepinv = 'keepInventory'
    deathmsg = 'showDeathMessages'
    admincmdlog = 'logAdminCommands'
    cmdlen = 'maxCommandChainLength'
    entcram = 'maxEntityCramming'
    mobgrief = 'mobGriefing'
    regen = 'naturalRegeneration'
    sleeppct = 'playersSleepingPercentage'
    rndtick = 'randomTickSpeed'
    spawnradius = 'spawnRadius'
    reducedf3 = 'reducedDebugInfo'
    spectchunkgen = 'spectatorsGenerateChunks'
    cmdfb = 'sendCommandFeedback'


class Gamemode(enum.IntEnum):

    """/gamemode numeric list"""

    survival = 0
    creative = 1
    adventure = 2
    spectator = 3


class Difficulty(enum.IntEnum):

    """/difficulty numeric list"""

    peaceful = 0
    easy = 1
    normal = 2
    hard = 3


# checking timezone format
tzcheck = re.compile(r'(^[A-Z]\w+\/[A-Z]\w+$)|^UTC$')

# options types converting
convert = {
    'config-option-number': int,
    'config-option-select': int,
    'config-option-toggle': bool,
}


class AternosConfig:

    """Class for editing server settings"""

    def __init__(self, atserv: 'AternosServer') -> None:
        """Class for editing server settings

        Args:
            atserv (python_aternos.atserver.AternosServer):
                atserver.AternosServer object
        """

        self.atserv = atserv

    def get_timezone(self) -> str:
        """Parses timezone from options page

        Returns:
            Area/Location
        """

        optreq = self.atserv.atserver_request(
            f'{BASE_URL}/options', 'GET'
        )
        opttree = lxml.html.fromstring(optreq)

        tzopt = opttree.xpath(
            '//div[@class="options-other-input timezone-switch"]'
        )[0]
        tztext = tzopt.xpath('.//div[@class="option current"]')[0].text
        return tztext.strip()

    def set_timezone(self, value: str) -> None:
        """Sets new timezone

        Args:
            value (str): New timezone

        Raises:
            ValueError: If given string doesn't
                match `Area/Location` format
        """

        matches_tz = tzcheck.search(value)
        if not matches_tz:
            raise ValueError(
                'Timezone must match zoneinfo format: Area/Location'
            )

        self.atserv.atserver_request(
            f'{AJAX_URL}/timezone.php',
            'POST', data={'timezone': value},
            sendtoken=True
        )

    def get_java(self) -> int:
        """Parses Java version from options page

        Returns:
            Java image version
        """

        optreq = self.atserv.atserver_request(
            f'{BASE_URL}/options', 'GET'
        )
        opttree = lxml.html.fromstring(optreq)
        imgopt = opttree.xpath(
            '//div[@class="options-other-input image-switch"]'
        )[0]
        imgver = imgopt.xpath(
            './/div[@class="option current"]/@data-value'
        )[0]

        jdkver = str(imgver or '').removeprefix('openjdk:')
        return int(jdkver)

    def set_java(self, value: int) -> None:
        """Sets new Java version

        Args:
            value (int): New Java image version
        """

        self.atserv.atserver_request(
            f'{AJAX_URL}/image.php',
            'POST', data={'image': f'openjdk:{value}'},
            sendtoken=True
        )

    #
    # server.properties
    #
    def set_server_prop(self, option: str, value: Any) -> None:
        """Sets server.properties option

        Args:
            option (str): Option name
            value (Any): New value
        """

        self.__set_prop(
            '/server.properties',
            option, value
        )

    def get_server_props(self, proptyping: bool = True) -> Dict[str, Any]:
        """Parses all server.properties from options page

        Args:
            proptyping (bool, optional):
                If the returned dict should
                contain value that matches
                property type (e.g. max-players will be int)
                instead of string

        Returns:
            `server.properties` dictionary
        """

        return self.__get_all_props(f'{BASE_URL}/options', proptyping)

    def set_server_props(self, props: Dict[str, Any]) -> None:
        """Updates server.properties options with the given dict

        Args:
            props (Dict[str,Any]):
                Dictionary with `{key:value}` properties
        """

        for key in props:
            self.set_server_prop(key, props[key])

    #
    # level.dat
    #
    def set_world_prop(
            self, option: Union[WorldOpts, WorldRules],
            value: Any, gamerule: bool = False,
            world: str = 'world') -> None:
        """Sets level.dat option for specified world

        Args:
            option (Union[WorldOpts, WorldRules]): Option name
            value (Any): New value
            gamerule (bool, optional): If the option is a gamerule
            world (str, optional): Name of the world which
                `level.dat` must be edited
        """

        prefix = DAT_PREFIX
        if gamerule:
            prefix = DAT_GR_PREFIX

        self.__set_prop(
            f'/{world}/level.dat',
            f'{prefix}{option}',
            value
        )

    def get_world_props(
            self, world: str = 'world',
            proptyping: bool = True) -> Dict[str, Any]:
        """Parses level.dat from specified world's options page

        Args:
            world (str, optional): Name of the worl
            proptyping (bool, optional):
                If the returned dict should
                contain the value that matches
                property type (e.g. randomTickSpeed will be bool)
                instead of string

        Returns:
            `level.dat` options dictionary
        """

        return self.__get_all_props(
            f'{BASE_URL}/files/{world}/level.dat',
            proptyping, [DAT_PREFIX, DAT_GR_PREFIX]
        )

    def set_world_props(
            self,
            props: Dict[Union[WorldOpts, WorldRules], Any],
            world: str = 'world') -> None:
        """Sets level.dat options from
        the dictionary for the specified world

        Args:
            props (Dict[Union[WorldOpts, WorldRules], Any]):
                `level.dat` options
            world (str): name of the world which
                `level.dat` must be edited
        """

        for key in props:
            self.set_world_prop(
                option=key,
                value=props[key],
                world=world
            )

    #
    # helpers
    #
    def __set_prop(self, file: str, option: str, value: Any) -> None:

        self.atserv.atserver_request(
            f'{AJAX_URL}/config.php',
            'POST', data={
                'file': file,
                'option': option,
                'value': value
            }, sendtoken=True
        )

    def __get_all_props(
            self, url: str, proptyping: bool = True,
            prefixes: Optional[List[str]] = None) -> Dict[str, Any]:

        optreq = self.atserv.atserver_request(url, 'GET')
        opttree = lxml.html.fromstring(optreq.content)
        configs = opttree.xpath('//div[@class="config-options"]')

        for i, conf in enumerate(configs):
            opts = conf.xpath('/div[contains(@class,"config-option ")]')
            result = {}

            for opt in opts:
                key = opt.xpath(
                    './/span[@class="config-option-output-key"]'
                )[0].text
                value = opt.xpath(
                    './/span[@class="config-option-output-value"]'
                )[0].text

                if prefixes is not None:
                    key = f'{prefixes[i]}{key}'

                opttype = opt.xpath('/@class').split(' ')[1]
                if proptyping and opttype in convert:
                    value = convert[opttype](value)

                result[key] = value

        return result

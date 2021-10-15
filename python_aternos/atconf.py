import re
import lxml.html
from typing import Any, Dict, List, Optional
from typing import TYPE_CHECKING

from . import atconnect

if TYPE_CHECKING:
	from atserver import AternosServer

OPT_PLAYERS = 'max-players'
OPT_GAMEMODE = 'gamemode'
OPT_DIFFICULTY = 'difficulty'
OPT_WHITELIST = 'white-list'
OPT_ONLINE = 'online-mode'
OPT_PVP = 'pvp'
OPT_CMDBLOCK = 'enable-command-block'
OPT_FLIGHT = 'allow-flight'
OPT_ANIMALS = 'spawn-animals'
OPT_MONSTERS = 'spawn-monsters'
OPT_VILLAGERS = 'spawn-npcs'
OPT_NETHER = 'allow-nether'
OPT_FORCEGM = 'force-gamemode'
OPT_SPAWNLOCK = 'spawn-protection'
OPT_CHEATS = 'allow-cheats'
OPT_RESOURCEPACK = 'resource-pack'

DAT_PREFIX = 'Data:'
DAT_SEED = 'RandomSeed'
DAT_HARDCORE = 'hardcore'
DAT_DIFFICULTY = 'Difficulty'

DAT_GR_PREFIX = 'Data:GameRules:'
DAT_GR_ADVS = 'announceAdvancements'
DAT_GR_CMDOUT = 'commandBlockOutput'
DAT_GR_ELYTRA = 'disableElytraMovementCheck'
DAT_GR_DAYLIGHT = 'doDaylightCycle'
DAT_GR_ENTDROPS = 'doEntityDrops'
DAT_GR_FIRETICK = 'doFireTick'
DAT_GR_LIMITCRAFT = 'doLimitedCrafting'
DAT_GR_MOBLOOT = 'doMobLoot'
DAT_GR_MOBS = 'doMobSpawning'
DAT_GR_TILEDROPS = 'doTileDrops'
DAT_GR_WEATHER = 'doWeatherCycle'
DAT_GR_KEEPINV = 'keepInventory'
DAT_GR_DEATHMSG = 'showDeathMessages'
DAT_GR_ADMINCMDLOG = 'logAdminCommands'
DAT_GR_CMDLEN = 'maxCommandChainLength'
DAT_GR_ENTCRAM = 'maxEntityCramming'
DAT_GR_MOBGRIEF = 'mobGriefing'
DAT_GR_REGEN = 'naturalRegeneration'
DAT_GR_RNDTICK = 'randomTickSpeed'
DAT_GR_SPAWNRADIUS = 'spawnRadius'
DAT_GR_REDUCEDF3 = 'reducedDebugInfo'
DAT_GR_SPECTCHUNK = 'spectatorsGenerateChunks'
DAT_GR_CMDFB = 'sendCommandFeedback'

DAT_TYPE_WORLD = 0
DAT_TYPE_GR = 1

GM_SURVIVAL = 0
GM_CREATIVE = 1
GM_ADVENTURE = 2
GM_SPECTATOR = 3

DF_PEACEFUL = 0
DF_EASY = 1
DF_NORMAL = 2
DF_HARD = 3

JAVA_JDK = 'openjdk:{}'
JAVA_OPENJ9 = 'adoptopenjdk:{}-jre-openj9-bionic'

FLAG_PROP_TYPE = 1

class AternosConfig:

	def __init__(self, atserv:'AternosServer') -> None:

		self.atserv = atserv

	@property
	def timezone(self) -> str:
		optreq = self.atserv.atserver_request(
			'https://aternos.org/options',
			atconnect.REQGET
		)
		opttree = lxml.html.fromstring(optreq)

		tzopt = opttree.xpath('//div[@class="options-other-input timezone-switch"]')[0]
		tztext = tzopt.xpath('.//div[@class="option current"]')[0].text
		return tztext.strip()

	@timezone.setter
	def timezone(self, value:str) -> None:
		matches_tz = re.search(r'(?:^[A-Z]\w+\/[A-Z]\w+$)|^UTC$', value)
		if matches_tz == None:
			raise AttributeError('Timezone must match zoneinfo format: Area/Location')

		self.atserv.atserver_request(
			'https://aternos.org/panel/ajax/timezone.php',
			atconnect.REQPOST, data={'timezone': value},
			sendtoken=True
		)

	@property
	def java_version(self) -> str:
		optreq = self.atserv.atserver_request(
			'https://aternos.org/options',
			atconnect.REQGET
		)
		opttree = lxml.html.fromstring(optreq)

		imgopt = opttree.xpath('//div[@class="options-other-input image-switch"]')[0]
		imgver = imgopt.xpath('.//div[@class="option current"]/@data-value')[0]
		return imgver

	@java_version.setter
	def java_version(self, value:str) -> None:
		matches_jdkver = re.search(r'^(?:adopt)*openjdk:(\d+)(?:-jre-openj9-bionic)*$', value)
		if matches_jdkver == None:
			raise AttributeError('Java image version must match "[adopt]openjdk:%d[-jre-openj9-bionic]" format')

		self.atserv.atserver_request(
			'https://aternos.org/panel/ajax/image.php',
			atconnect.REQPOST, data={'image': value},
			sendtoken=True
		)

	#
	# server.properties
	#
	def set_server_prop(self, option:str, value:Any) -> None:
		self.__set_prop(
			'/server.properties',
			option, value
		)

	def get_server_props(self, flags:int=FLAG_PROP_TYPE) -> Dict[str,Any]:
		return self.__get_all_props('https://aternos.org/options', flags)

	def set_server_props(self, props:Dict[str,Any]) -> None:
		for key in props:
			set_server_prop(key, props[key])

	#
	# level.dat
	#
	def set_world_prop(
		self, option:str, value:Any,
		proptype:int, world:str='world') -> None:
		prefix = DAT_PREFIX
		if proptype == DAT_TYPE_GR:
			prefix = DAT_GR_PREFIX

		self.__set_prop(
			f'/{world}/level.dat',
			f'{prefix}{option}',
			value
		)

	def get_world_props(
		self, world:str='world',
		flags:int=FLAG_PROP_TYPE) -> Dict[str,Any]:
		self.__get_all_props(
			f'https://aternos.org/files/{world}/level.dat',
			flags, [DAT_PREFIX, DAT_GR_PREFIX]
		)

	def set_world_props(self, props:Dict[str,Any]) -> None:
		for key in props:
			set_world_prop(key, prop[key])

	#
	# helpers
	#
	def __set_prop(self, file:str, option:str, value:Any) -> None:

		self.atserv.atserver_request(
			'https://aternos.org/panel/ajax/config.php',
			atconnect.REQPOST, data={
				'file': file,
				'option': option,
				'value': value
			}, sendtoken=True
		)

	def __get_all_props(
		self, url:str, flags:int=FLAG_PROP_TYPE,
		prefixes:Optional[List[str]]=None) -> Dict[str,Any]:

		optreq = self.atserv.atserver_request(
			'https://aternos.org/options',
			atconnect.REQGET
		)
		opttree = lxml.html.fromstring(optreq.content)

		configs = opttree.xpath('//div[@class="config-options"]')
		for i in range(len(configs)):

			conf = configs[i]
			opts = conf.xpath('/div[contains(@class,"config-option ")]')
			result = {}

			for opt in opts:

				key = opt.xpath('.//span[@class="config-option-output-key"]')[0].text
				value = opt.xpath('.//span[@class="config-option-output-value"]')[0].text
				if prefixes != None:
					key = f'{prefixes[i]}{key}'

				opttype = opt.xpath('/@class').split(' ')[1]
				if flags == FLAG_PROP_TYPE:

					if opttype == 'config-option-number'\
					or opttype == 'config-option-select':
						value = int(value)

					elif opttype == 'config-option-toggle':
						value = bool(value)
				result[key] = value
		return result

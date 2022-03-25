import enum
import re
import lxml.html
from typing import Any, Dict, List, Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from .atserver import AternosServer

#
# server.options
class ServerOpts(enum.Enum):
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

DAT_PREFIX = 'Data:'
DAT_GR_PREFIX = 'Data:GameRules:'

# level.dat
class WorldOpts(enum.Enum):
	seed12 = 'randomseed'
	seed = 'seed'
	hardcore = 'hardcore'
	difficulty = 'Difficulty'

# /gamerule
class WorldRules(enum.Enum):
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

DAT_TYPE_WORLD = 0
DAT_TYPE_GR = 1

class Gamemode(enum.IntEnum):
	survival = 0
	creative = 1
	adventure = 2
	spectator = 3

class Difficulty(enum.IntEnum):
	peaceful = 0
	easy = 1
	normal = 2
	hard = 3

#
# jre types for set_java
javatype = {
	'jdk': 'openjdk:{ver}',
	'openj9-1': 'adoptopenjdk:{ver}-jre-openj9-bionic',
	'openj9-2': 'ibm-semeru-runtimes:open-{ver}-jre'
}
# checking java version format
javacheck = re.compile(
	''.join(
		list(
			map(
				# create a regexp for each jre type,
				# e.g.: (^openjdk:\d+$)|
				lambda i: '(^' + javatype[i].format(ver=r'\d+') + '$)|',
				javatype
			)
		)
	).rstrip('|')
)
# checking timezone format
tzcheck = re.compile(r'(^[A-Z]\w+\/[A-Z]\w+$)|^UTC$')
# options types converting
convert = {
	'config-option-number': int,
	'config-option-select': int,
	'config-option-toggle': bool
}

# MAIN CLASS
class AternosConfig:

	def __init__(self, atserv:'AternosServer') -> None:

		self.atserv = atserv

	def get_timezone(self) -> str:

		optreq = self.atserv.atserver_request(
			'https://aternos.org/options', 'GET'
		)
		opttree = lxml.html.fromstring(optreq)

		tzopt = opttree.xpath('//div[@class="options-other-input timezone-switch"]')[0]
		tztext = tzopt.xpath('.//div[@class="option current"]')[0].text
		return tztext.strip()

	def set_timezone(self, value:str) -> None:

		matches_tz = tzcheck.search(value)
		if not matches_tz:
			raise ValueError('Timezone must match zoneinfo format: Area/Location')

		self.atserv.atserver_request(
			'https://aternos.org/panel/ajax/timezone.php',
			'POST', data={'timezone': value},
			sendtoken=True
		)

	def get_java(self) -> str:

		optreq = self.atserv.atserver_request(
			'https://aternos.org/options', 'GET'
		)
		opttree = lxml.html.fromstring(optreq)
		imgopt = opttree.xpath('//div[@class="options-other-input image-switch"]')[0]
		imgver = imgopt.xpath('.//div[@class="option current"]/@data-value')[0]
		return imgver

	def set_java(self, value:str) -> None:

		matches_jdkver = javacheck.search(value)
		if not matches_jdkver:
			raise ValueError('Incorrect Java image version format!')

		self.atserv.atserver_request(
			'https://aternos.org/panel/ajax/image.php',
			'POST', data={'image': value},
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

	def get_server_props(self, proptyping:bool=True) -> Dict[str,Any]:
		return self.__get_all_props('https://aternos.org/options', proptyping)

	def set_server_props(self, props:Dict[str,Any]) -> None:
		for key in props:
			self.set_server_prop(key, props[key])

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
		proptyping:bool=True) -> Dict[str,Any]:

		self.__get_all_props(
			f'https://aternos.org/files/{world}/level.dat',
			proptyping, [DAT_PREFIX, DAT_GR_PREFIX]
		)

	def set_world_props(self, props:Dict[str,Any]) -> None:
		for key in props:
			self.set_world_prop(key, props[key])

	#
	# helpers
	#
	def __set_prop(self, file:str, option:str, value:Any) -> None:

		self.atserv.atserver_request(
			'https://aternos.org/panel/ajax/config.php',
			'POST', data={
				'file': file,
				'option': option,
				'value': value
			}, sendtoken=True
		)

	def __get_all_props(
		self, url:str, proptyping:bool=True,
		prefixes:Optional[List[str]]=None) -> Dict[str,Any]:

		optreq = self.atserv.atserver_request(url, 'GET')
		opttree = lxml.html.fromstring(optreq.content)
		configs = opttree.xpath('//div[@class="config-options"]')

		for i, conf in enumerate(configs):
			opts = conf.xpath('/div[contains(@class,"config-option ")]')
			result = {}

			for opt in opts:
				key = opt.xpath('.//span[@class="config-option-output-key"]')[0].text
				value = opt.xpath('.//span[@class="config-option-output-value"]')[0].text

				if prefixes != None:
					key = f'{prefixes[i]}{key}'

				opttype = opt.xpath('/@class').split(' ')[1]
				if proptyping and opttype in convert:
					value = convert[opttype](value)

				result[key] = value

		return result

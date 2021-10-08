from . import atconnect

class AternosFileManager:

	def __init__(atserv):

		self.atserv = atserv

	def listdir(self, path=''):

		self.atserv.atserver_request(
			f'https://aternos.org/files/{path}',
			atconnect.AternosConnect.REQGET
		)

	def get_file(self, path):

		self.atserv.atserver_request(
			f'https://aternos.org/panel/ajax/files/download.php?file={path}',
			atconnect.AternosConnect.REQGET
		)

	def get_world(self, world):

		self.atserv.atserver_request(
			f'https://aternos.org/panel/ajax/worlds/download.php?world={world}',
			atconnect.AternosConnect.REQGET
		)

import lxml.html
from typing import Union
from typing import TYPE_CHECKING

from . import atconnect

if TYPE_CHECKING:
	from atserver import AternosServer

FTYPE_FILE = 0
FTYPE_DIR = 1

class AternosFile:

	def __init__(
		self, atserv:'AternosServer',
		path:str, name:str, ftype:int=FTYPE_FILE,
		size:Union[int,float]=0, dlallowed:bool=False) -> None:

		self.atserv = atserv
		self._path = path
		self._name = name
		self._ftype = ftype
		self._size = float(size)
		self._dlallowed = dlallowed

	def delete(self) -> None:

		self.atserv.atserver_request(
			'https://aternos.org/panel/ajax/delete.php',
			atconnect.REQPOST, data={'file': self._name},
			sendtoken=True
		)

	@property
	def content(self) -> bytes:
		file = self.atserv.atserver_request(
			f'https://aternos.org/panel/ajax/files/download.php',
			atconnect.REQGET, params={'file': self.path.replace('/','%2F')}
		)
		if not self._dlallowed:
			raise AternosIOError('Downloading this file is not allowed. Try to get text')
		return file.content

	@content.setter
	def content(self, value:bytes) -> None:
		self.atserv.atserver_request(
			f'https://aternos.org/panel/ajax/save.php',
			atconnect.REQPOST, data={'content': value},
			sendtoken=True
		)

	@property
	def text(self) -> str:
		editor = self.atserv.atserver_request(
			f'https://aternos.org/files/{self._name}',
			atconnect.REQGET
		)
		edittree = lxml.html.fromstring(editor.content)

		editfield = edittree.xpath('//div[@class="ace_layer ace_text-layer"]')[0]
		editlines = editfield.xpath('/div[@class="ace_line"]')
		rawlines = []

		for line in editlines:
			rawlines.append(line.text)
		return rawlines

	@text.setter
	def text(self, value:str) -> None:
		self.atserv.atserver_request(
			f'https://aternos.org/panel/ajax/save.php',
			atconnect.REQPOST, data={'content': value},
			sendtoken=True
		)

	@property
	def path(self):
		return self._path

	@property
	def name(self) -> str:
		return self._name

	@property
	def is_dir(self) -> bool:
		if self._ftype == FTYPE_DIR:
			return True
		return False

	@property
	def is_file(self) -> bool:
		if self._ftype == FTYPE_FILE:
			return True
		return False
	
	@property
	def size(self) -> float:
		return self._size

	@property
	def dlallowed(self) -> bool:
		return self._dlallowed

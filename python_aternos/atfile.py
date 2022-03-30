import enum
import lxml.html
from typing import Union
from typing import TYPE_CHECKING

from .aterrors import FileError

if TYPE_CHECKING:
	from .atserver import AternosServer

class FileType(enum.IntEnum):
	file = 0
	directory = 1

class AternosFile:

	def __init__(
		self, atserv:'AternosServer',
		path:str, name:str, ftype:int=FileType.file,
		size:Union[int,float]=0) -> None:

		self.atserv = atserv
		self._path = path.lstrip('/')
		self._name = name
		self._full = path + name
		self._ftype = ftype
		self._size = float(size)

	def delete(self) -> None:

		self.atserv.atserver_request(
			'https://aternos.org/panel/ajax/delete.php',
			'POST', data={'file': self._full},
			sendtoken=True
		)

	def get_content(self) -> bytes:

		file = self.atserv.atserver_request(
			'https://aternos.org/panel/ajax/files/download.php',
			'GET', params={
				'file': self._full
			}
		)
		if file.content == b'{"success":false}':
			raise FileError('Unable to download the file. Try to get text')
		return file.content

	def set_content(self, value:bytes) -> None:

		self.atserv.atserver_request(
			f'https://aternos.org/panel/ajax/save.php',
			'POST', data={
				'file': self._full,
				'content': value
			}, sendtoken=True
		)

	def get_text(self) -> str:

		editor = self.atserv.atserver_request(
			f'https://aternos.org/files/{self._full}', 'GET'
		)
		edittree = lxml.html.fromstring(editor.content)

		editlines = edittree.xpath('//div[@class="ace_line"]')
		rawlines = []

		for line in editlines:
			rawlines.append(line.text)
		return rawlines

	def set_text(self, value:str) -> None:
		
		self.set_content(value.encode('utf-8'))

	@property
	def path(self):
		return self._path

	@property
	def name(self) -> str:
		return self._name
	
	@property
	def full(self) -> str:
		return self._full

	@property
	def is_dir(self) -> bool:
		if self._ftype == FileType.directory:
			return True
		return False

	@property
	def is_file(self) -> bool:
		if self._ftype == FileType.file:
			return True
		return False
	
	@property
	def size(self) -> float:
		return self._size

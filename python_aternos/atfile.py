import enum
import lxml.html
from typing import Union
from typing import TYPE_CHECKING

from .aterrors import FileError

if TYPE_CHECKING:
    from .atserver import AternosServer


class FileType(enum.IntEnum):

    """File or dierctory"""

    file = 0
    directory = 1


class AternosFile:

    """File class which contains info about its path, type and size

    :param atserv: :class:`python_aternos.atserver.AternosServer` instance
    :type atserv: python_aternos.atserver.AternosServer
    :param path: Path to the file
    :type path: str
    :param name: Filename
    :type name: str
    :param ftype: File or directory
    :type ftype: python_aternos.atfile.FileType
    :param size: File size, defaults to 0
    :type size: Union[int,float], optional
    """

    def __init__(
            self,
            atserv: 'AternosServer',
            path: str, name: str,
            ftype: FileType = FileType.file,
            size: Union[int, float] = 0) -> None:

        self.atserv = atserv
        self._path = path.lstrip('/')
        self._name = name
        self._full = path + name
        self._ftype = ftype
        self._size = float(size)

    def delete(self) -> None:

        """Deletes the file"""

        self.atserv.atserver_request(
            'https://aternos.org/panel/ajax/delete.php',
            'POST', data={'file': self._full},
            sendtoken=True
        )

    def get_content(self) -> bytes:

        """Requests file content in bytes (downloads it)

        :raises FileError: If downloading
        the file is not allowed by Aternos
        :return: File content
        :rtype: bytes
        """

        file = self.atserv.atserver_request(
            'https://aternos.org/panel/ajax/files/download.php',
            'GET', params={
                'file': self._full
            }
        )
        if file.content == b'{"success":false}':
            raise FileError('Unable to download the file. Try to get text')
        return file.content

    def set_content(self, value: bytes) -> None:

        """Modifies the file content

        :param value: New content
        :type value: bytes
        """

        self.atserv.atserver_request(
            f'https://aternos.org/panel/ajax/save.php',
            'POST', data={
                'file': self._full,
                'content': value
            }, sendtoken=True
        )

    def get_text(self) -> str:

        """Requests editing the file as a text
        (try it if downloading is disallowed)

        :return: File text content
        :rtype: str
        """

        editor = self.atserv.atserver_request(
            f'https://aternos.org/files/{self._full.lstrip("/")}', 'GET'
        )
        edittree = lxml.html.fromstring(editor.content)

        editblock = edittree.xpath('//div[@id="editor"]')[0]
        return editblock.text_content()

    def set_text(self, value: str) -> None:

        """Modifies the file content,
        but unlike set_content takes
        a string as a new value

        :param value: New content
        :type value: str
        """

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

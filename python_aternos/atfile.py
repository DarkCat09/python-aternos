"""File info object used by `python_aternos.atfm`"""

import enum

from typing import Union
from typing import TYPE_CHECKING

import lxml.html

from .atconnect import BASE_URL, AJAX_URL
from .aterrors import FileError

if TYPE_CHECKING:
    from .atserver import AternosServer


class FileType(enum.IntEnum):

    """File or dierctory"""

    file = 0
    directory = 1
    dir = 1


class AternosFile:

    """File class which contains info
    about its path, type and size"""

    def __init__(
            self,
            atserv: 'AternosServer',
            path: str, rmable: bool,
            dlable: bool, editable: bool,
            ftype: FileType = FileType.file,
            size: Union[int, float] = 0) -> None:
        """File class which contains info
        about its path, type and size

        Args:
            atserv (python_aternos.atserver.AternosServer):
                atserver.AternosServer instance
            path (str): Absolute path to the file
            rmable (bool): Is the file deleteable (removeable)
            dlable (bool): Is the file downloadable
            ftype (python_aternos.atfile.FileType): File or directory
            size (Union[int,float], optional): File size
        """

        path = path.lstrip('/')
        path = '/' + path

        self.atserv = atserv

        self._path = path
        self._name = path[path.rfind('/') + 1:]
        self._dirname = path[:path.rfind('/')]

        self._deleteable = rmable
        self._downloadable = dlable
        self._editable = editable

        self._ftype = ftype
        self._size = float(size)

    def create(
            self,
            name: str,
            ftype: FileType = FileType.file) -> None:
        """Creates a file or a directory inside this one

        Args:
            name (str): Filename
            ftype (FileType, optional): File type

        Raises:
            RuntimeWarning: Messages about probabilty of FileError
                (if `self` file object is not a directory)
            FileError: If Aternos denied file creation
        """

        if self.is_file:
            raise RuntimeWarning(
                'Creating files only available '
                'inside directories'
            )

        name = name.strip().replace('/', '_')
        req = self.atserv.atserver_request(
            f'{AJAX_URL}/files/create.php',
            'POST', data={
                'file': f'{self._path}/{name}',
                'type': 'file'
                if ftype == FileType.file
                else 'directory'
            }
        )

        if req.content == b'{"success":false}':
            raise FileError('Unable to create a file')

    def delete(self) -> None:
        """Deletes the file

        Raises:
            RuntimeWarning: Message about probability of FileError
            FileError: If deleting this file is disallowed by Aternos
        """

        if not self._deleteable:
            raise RuntimeWarning(
                'The file seems to be protected (undeleteable). '
                'Always check it before calling delete()'
            )

        req = self.atserv.atserver_request(
            f'{AJAX_URL}/delete.php',
            'POST', data={'file': self._path},
            sendtoken=True
        )

        if req.content == b'{"success":false}':
            raise FileError('Unable to delete the file')

    def get_content(self) -> bytes:
        """Requests file content in bytes (downloads it)

        Raises:
            RuntimeWarning: Message about probability of FileError
            FileError: If downloading this file is disallowed by Aternos

        Returns:
            File content
        """

        if not self._downloadable:
            raise RuntimeWarning(
                'The file seems to be undownloadable. '
                'Always check it before calling get_content()'
            )

        file = self.atserv.atserver_request(
            f'{AJAX_URL}/files/download.php',
            'GET', params={
                'file': self._path
            }
        )

        if file.content == b'{"success":false}':
            raise FileError(
                'Unable to download the file. '
                'Try to get text'
            )

        return file.content

    def set_content(self, value: bytes) -> None:
        """Modifies file content

        Args:
            value (bytes): New content

        Raises:
            FileError: If Aternos denied file saving
        """

        req = self.atserv.atserver_request(
            f'{AJAX_URL}/save.php',
            'POST', data={
                'file': self._path,
                'content': value
            }, sendtoken=True
        )

        if req.content == b'{"success":false}':
            raise FileError('Unable to save the file')

    def get_text(self) -> str:
        """Requests editing the file as a text

        Raises:
            RuntimeWarning: Message about probability of FileError
            FileError: If unable to parse text from response

        Returns:
            File text content
        """

        if not self._editable:
            raise RuntimeWarning(
                'The file seems to be uneditable. '
                'Always check it before calling get_text()'
            )

        if self.is_dir:
            raise RuntimeWarning(
                'Use get_content() to download '
                'a directory as a ZIP file!'
            )

        filepath = self._path.lstrip("/")
        editor = self.atserv.atserver_request(
            f'{BASE_URL}/files/{filepath}', 'GET'
        )
        edittree = lxml.html.fromstring(editor.content)
        editblock = edittree.xpath('//div[@id="editor"]')

        if len(editblock) < 1:
            raise FileError(
                'Unable to open editor. '
                'Try to get file content'
            )

        return editblock[0].text_content()

    def set_text(self, value: str) -> None:
        """Modifies the file content,
        but unlike `set_content` takes
        a string as an argument

        Args:
            value (str): New content
        """

        self.set_content(value.encode('utf-8'))

    @property
    def path(self) -> str:
        """Abslute path to the file
        without leading slash
        including filename

        Returns:
            Full path to the file
        """

        return self._path

    @property
    def name(self) -> str:
        """Filename with extension

        Returns:
            Filename
        """

        return self._name

    @property
    def dirname(self) -> str:
        """Full path to the directory
        which contains the file
        without leading slash.
        Empty path means root (`/`)

        Returns:
            Path to the directory
        """

        return self._dirname

    @property
    def deleteable(self) -> bool:
        """True if the file can be deleted,
        otherwise False

        Returns:
            Can the file be deleted
        """

        return self._deleteable

    @property
    def downloadable(self) -> bool:
        """True if the file can be downloaded,
        otherwise False

        Returns:
            Can the file be downloaded
        """

        return self._downloadable

    @property
    def editable(self) -> bool:
        """True if the file can be
        opened in Aternos editor,
        otherwise False

        Returns:
            Can the file be edited
        """

        return self._editable

    @property
    def ftype(self) -> FileType:
        """File object type: file or directory

        Returns:
            File type
        """

        return self._ftype

    @property
    def is_dir(self) -> bool:
        """Check if the file object is a directory

        Returns:
            True if it is a directory, otherwise False
        """

        return self._ftype == FileType.dir

    @property
    def is_file(self) -> bool:
        """Check if the file object is not a directory

        Returns:
            True if it is a file, otherwise False
        """

        return self._ftype == FileType.file

    @property
    def size(self) -> float:
        """File size in bytes

        Returns:
            File size
        """

        return self._size

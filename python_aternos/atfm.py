import lxml.html
from typing import Union, Optional, List
from typing import TYPE_CHECKING

from .atfile import AternosFile, FileType
if TYPE_CHECKING:
    from .atserver import AternosServer


class FileManager:

    """Aternos file manager class for viewing files structure

    :param atserv: :class:`python_aternos.atserver.AternosServer` instance
    :type atserv: python_aternos.atserver.AternosServer
    """

    def __init__(self, atserv: 'AternosServer') -> None:

        self.atserv = atserv

    def listdir(self, path: str = '') -> List[AternosFile]:

        """Requests a list of files
        in the specified directory

        :param path: Directory
        (an empty string means root), defaults to ''
        :type path: str, optional
        :return: List of :class:`python_aternos.atfile.AternosFile`
        :rtype: List[AternosFile]
        """

        path = path.lstrip('/')
        filesreq = self.atserv.atserver_request(
            f'https://aternos.org/files/{path}', 'GET'
        )
        filestree = lxml.html.fromstring(filesreq.content)
        fileslist = filestree.xpath(
            '//div[contains(concat(" ",normalize-space(@class)," ")," file ")]'
        )

        files = []
        for f in fileslist:

            ftype_raw = f.xpath('@data-type')[0]
            ftype = FileType.file \
                if ftype_raw == 'file' \
                else FileType.directory

            fsize_raw = f.xpath('./div[@class="filesize"]')
            fsize = 0.0
            if len(fsize_raw) > 0:

                fsize_text = fsize_raw[0].text.strip()
                fsize_num = fsize_text[:fsize_text.rfind(' ')]
                fsize_msr = fsize_text[fsize_text.rfind(' ')+1:]

                try:
                    fsize = self.convert_size(float(fsize_num), fsize_msr)
                except ValueError:
                    fsize = -1

            fullpath = f.xpath('@data-path')[0]
            filepath = fullpath[:fullpath.rfind('/')]
            filename = fullpath[fullpath.rfind('/'):]
            files.append(
                AternosFile(
                    self.atserv,
                    filepath, filename,
                    ftype, fsize
                )
            )

        return files

    def convert_size(self, num: Union[int, float], measure: str) -> float:

        """Converts "human" file size to size in bytes

        :param num: Size
        :type num: Union[int,float]
        :param measure: Units (B, kB, MB, GB)
        :type measure: str
        :return: Size in bytes
        :rtype: float
        """

        measure_match = {
            'B': 1,
            'kB': 1000,
            'MB': 1000000,
            'GB': 1000000000
        }
        try:
            return num * measure_match[measure]
        except KeyError:
            return -1

    def get_file(self, path: str) -> Optional[AternosFile]:

        """Returns :class:`python_aternos.atfile.AternosFile`
        instance by its path

        :param path: Path to file including its filename
        :type path: str
        :return: _description_
        :rtype: Optional[AternosFile]
        """

        filepath = path[:path.rfind('/')]
        filename = path[path.rfind('/'):]

        filedir = self.listdir(filepath)
        for file in filedir:
            if file.name == filename:
                return file

        return None

    def dl_file(self, path: str) -> bytes:

        """Returns the file content in bytes (downloads it)

        :param path: Path to file including its filename
        :type path: str
        :return: File content
        :rtype: bytes
        """

        file = self.atserv.atserver_request(
            'https://aternos.org/panel/ajax/files/download.php'
            'GET', params={
                'file': path.replace('/', '%2F')
            }
        )

        return file.content

    def dl_world(self, world: str = 'world') -> bytes:

        """Returns the world zip file content
        by its name (downloads it)

        :param world: Name of world, defaults to 'world'
        :type world: str, optional
        :return: Zip file content
        :rtype: bytes
        """

        world = self.atserv.atserver_request(
            'https://aternos.org/panel/ajax/worlds/download.php'
            'GET', params={
                'world': world.replace('/', '%2F')
            }
        )

        return world.content

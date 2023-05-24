"""Exploring files in your server directory"""

from typing import Union, Optional, Any, List
from typing import TYPE_CHECKING

import lxml.html

from .atconnect import BASE_URL, AJAX_URL
from .atfile import AternosFile, FileType

if TYPE_CHECKING:
    from .atserver import AternosServer


class FileManager:

    """Aternos file manager class
    for viewing files structure"""

    def __init__(self, atserv: 'AternosServer') -> None:
        """Aternos file manager class
        for viewing files structure

        Args:
            atserv (python_aternos.atserver.AternosServer):
                atserver.AternosServer instance
        """

        self.atserv = atserv

    def list_dir(self, path: str = '') -> List[AternosFile]:
        """Requests a list of files
        in the specified directory

        Args:
            path (str, optional):
                Directory (an empty string means root)

        Returns:
            List of atfile.AternosFile objects
        """

        path = path.lstrip('/')

        filesreq = self.atserv.atserver_request(
            f'{BASE_URL}/files/{path}', 'GET'
        )
        filestree = lxml.html.fromstring(filesreq.content)

        fileslist = filestree.xpath(
            '//div[@class="file" or @class="file clickable"]'
        )

        files = []
        for f in fileslist:

            ftype_raw = f.xpath('@data-type')[0]
            fsize = self.extract_size(
                f.xpath('./div[@class="filesize"]')
            )

            rm_btn = f.xpath('./div[contains(@class,"js-delete-file")]')
            dl_btn = f.xpath('./div[contains(@class,"js-download-file")]')
            clickable = 'clickable' in f.classes
            is_config = ('server.properties' in path) or ('level.dat' in path)

            files.append(
                AternosFile(
                    atserv=self.atserv,
                    path=f.xpath('@data-path')[0],

                    rmable=(len(rm_btn) > 0),
                    dlable=(len(dl_btn) > 0),
                    editable=(clickable and not is_config),

                    ftype={'file': FileType.file}.get(
                        ftype_raw, FileType.dir
                    ),
                    size=fsize
                )
            )

        return files

    def extract_size(self, fsize_raw: List[Any]) -> float:
        """Parses file size from the LXML tree

        Args:
            fsize_raw (List[Any]): XPath parsing result

        Returns:
            File size in bytes
        """

        if len(fsize_raw) > 0:

            fsize_text = fsize_raw[0].text.strip()
            fsize_num = fsize_text[:fsize_text.rfind(' ')]
            fsize_msr = fsize_text[fsize_text.rfind(' ') + 1:]

            try:
                return self.convert_size(
                    float(fsize_num),
                    fsize_msr
                )
            except ValueError:
                return -1.0

        return 0.0

    def convert_size(
            self,
            num: Union[int, float],
            measure: str) -> float:
        """Converts "human" file size to size in bytes

        Args:
            num (Union[int,float]): Size
            measure (str): Units (B, kB, MB, GB)

        Returns:
            Size in bytes
        """

        measure_match = {
            'B': 1,
            'kB': 1000,
            'MB': 1000000,
            'GB': 1000000000
        }
        return measure_match.get(measure, -1) * num

    def get_file(self, path: str) -> Optional[AternosFile]:
        """Returns :class:`python_aternos.atfile.AternosFile`
        instance by its path

        Args:
            path (str): Path to the file including its filename

        Returns:
            atfile.AternosFile object
            if file has been found,
            otherwise None
        """

        filedir = path[:path.rfind('/')]
        filename = path[path.rfind('/'):]

        files = self.list_dir(filedir)

        return {
            'file': f
            for f in files
            if f.name == filename
        }.get('file', None)

    def dl_file(self, path: str) -> bytes:
        """Returns the file content in bytes (downloads it)

        Args:
            path (str): Path to file including its filename

        Returns:
            File content
        """

        file = self.atserv.atserver_request(  # type: ignore
            f'{AJAX_URL}/files/download.php'
            'GET', params={
                'file': path.replace('/', '%2F')
            }
        )

        return file.content

    def dl_world(self, world: str = 'world') -> bytes:
        """Returns the world zip file content
        by its name (downloads it)

        Args:
            world (str, optional): Name of world

        Returns:
            ZIP file content
        """

        resp = self.atserv.atserver_request(  # type: ignore
            f'{AJAX_URL}/worlds/download.php'
            'GET', params={
                'world': world.replace('/', '%2F')
            }
        )

        return resp.content

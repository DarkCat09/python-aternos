"""
Unofficial Aternos API module written in Python.
It uses Aternos' private API and html parsing"""

from .atclient import Client
from .atserver import AternosServer
from .atserver import Edition
from .atserver import Status
from .atconnect import AternosConnect
from .atplayers import PlayersList
from .atplayers import Lists
from .atconf import AternosConfig
from .atconf import ServerOpts
from .atconf import WorldOpts
from .atconf import WorldRules
from .atconf import Gamemode
from .atconf import Difficulty
from .atwss import AternosWss
from .atwss import Streams
from .atfm import FileManager
from .atfile import AternosFile
from .atfile import FileType
from .aterrors import AternosError
from .aterrors import CloudflareError
from .aterrors import CredentialsError
from .aterrors import TokenError
from .aterrors import ServerError
from .aterrors import ServerStartError
from .aterrors import FileError
from .aterrors import AternosPermissionError
from .atjsparse import exec_js

__all__ = [

    'atclient', 'atserver', 'atconnect',
    'atplayers', 'atconf', 'atwss',
    'atfm', 'atfile',
    'aterrors', 'atjsparse',

    'Client', 'AternosServer', 'AternosConnect',
    'PlayersList', 'AternosConfig', 'AternosWss',
    'FileManager', 'AternosFile', 'AternosError',
    'CloudflareError', 'CredentialsError', 'TokenError',
    'ServerError', 'ServerStartError', 'FileError',
    'AternosPermissionError', 'exec_js',

    'Edition', 'Status', 'Lists',
    'ServerOpts', 'WorldOpts', 'WorldRules',
    'Gamemode', 'Difficulty', 'Streams', 'FileType',
]

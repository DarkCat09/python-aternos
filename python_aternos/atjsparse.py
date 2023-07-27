"""Parsing and executing JavaScript code"""

import abc

import json
import base64

import subprocess

from pathlib import Path
from typing import Optional, Union
from typing import Type, Any

import regex
import js2py
import requests

from .atlog import log


js: Optional['Interpreter'] = None


class Interpreter(abc.ABC):
    """Base JS interpreter class"""

    def __init__(self) -> None:
        """Base JS interpreter class"""

    def __getitem__(self, name: str) -> Any:
        """Support for `js[name]` syntax
        instead of `js.get_var(name)`

        Args:
            name (str): Variable name

        Returns:
            Variable value
        """
        return self.get_var(name)

    @abc.abstractmethod
    def exec_js(self, func: str) -> None:
        """Executes JavaScript code

        Args:
            func (str): JS function
        """

    @abc.abstractmethod
    def get_var(self, name: str) -> Any:
        """Returns JS variable value
        from the interpreter

        Args:
            name (str): Variable name

        Returns:
            Variable value
        """


class NodeInterpreter(Interpreter):
    """Node.JS interpreter wrapper,
    starts a simple web server in background"""

    def __init__(
            self,
            node: Union[str, Path] = 'node',
            host: str = 'localhost',
            port: int = 8001) -> None:
        """Node.JS interpreter wrapper,
        starts a simple web server in background

        Args:
            node (Union[str, Path], optional): Path to `node` executable
            host (str, optional): Hostname for the web server
            port (int, optional): Port for the web server
        """

        super().__init__()

        file_dir = Path(__file__).absolute().parent
        server_js = file_dir / 'data' / 'server.js'

        self.url = f'http://{host}:{port}'
        self.timeout = 2

        # pylint: disable=consider-using-with
        self.proc = subprocess.Popen(
            args=[
                node, server_js,
                f'{port}', host,
            ],
            stdout=subprocess.PIPE,
        )
        # pylint: enable=consider-using-with

        assert self.proc.stdout is not None
        ok_msg = self.proc.stdout.readline()
        log.debug('Received from server.js: %s', ok_msg)

    def exec_js(self, func: str) -> None:
        resp = requests.post(self.url, data=func, timeout=self.timeout)
        resp.raise_for_status()

    def get_var(self, name: str) -> Any:
        resp = requests.post(self.url, data=name, timeout=self.timeout)
        resp.raise_for_status()
        log.debug('NodeJS response: %s', resp.content)
        return json.loads(resp.content)

    def __del__(self) -> None:
        try:
            self.proc.terminate()
            self.proc.communicate()
        except AttributeError:
            log.warning(
                'NodeJS process was not initialized, '
                'but __del__ was called'
            )


class Js2PyInterpreter(Interpreter):
    """Js2Py interpreter,
    uses js2py library to execute code"""

    # Thanks to http://regex.inginf.units.it
    arrowexp = regex.compile(r'\w[^\}]*+')

    def __init__(self) -> None:
        """Js2Py interpreter,
        uses js2py library to execute code"""

        super().__init__()

        ctx = js2py.EvalJs({'atob': atob})
        ctx.execute('''
        window.Map = function(_i){ };
        window.setTimeout = function(_f,_t){ };
        window.setInterval = function(_f,_t){ };
        window.encodeURIComponent = window.Map;
        window.document = { };
        document.doctype = { };
        document.currentScript = { };
        document.getElementById = window.Map;
        document.prepend = window.Map;
        document.append = window.Map;
        document.appendChild = window.Map;
        ''')

        self.ctx = ctx

    def exec_js(self, func: str) -> None:
        self.ctx.execute(self.to_ecma5(func))

    def get_var(self, name: str) -> Any:
        return self.ctx[name]

    def to_ecma5(self, func: str) -> str:
        """Converts from ECMA6 format to ECMA5
        (replacing arrow expressions)
        and removes comment blocks

        Args:
            func (str): ECMA6 function

        Returns:
            ECMA5 function
        """

        # Delete anything between /* and */
        func = regex.sub(r'/\*.+?\*/', '', func)

        # Search for arrow expressions
        match = self.arrowexp.search(func)
        if match is None:
            return func

        # Convert the function
        conv = '(function(){' + match[0] + '})()'

        # Convert 1 more expression.
        # It doesn't change,
        # so it was hardcoded
        # as a regexp
        return regex.sub(
            r'(?:s|\(s\)) => s.split\([\'"]{2}\).reverse\(\).join\([\'"]{2}\)',
            'function(s){return s.split(\'\').reverse().join(\'\')}',
            conv
        )


def atob(s: str) -> str:
    """Wrapper for the built-in library function.
    Decodes a base64 string

    Args:
        s (str): Encoded data

    Returns:
        Decoded string
    """

    return base64.standard_b64decode(str(s)).decode('utf-8')


def get_interpreter(
        *args,
        create: Type[Interpreter] = Js2PyInterpreter,
        **kwargs) -> 'Interpreter':
    """Get or create a JS interpreter.
    `*args` and `**kwargs` will be passed
    directly to JS interpreter `__init__`
    (when creating it)

    Args:
        create (Type[Interpreter], optional): Preferred interpreter

    Returns:
        JS interpreter instance
    """

    global js  # pylint: disable=global-statement

    # create if none
    if js is None:
        js = create(*args, **kwargs)

    # and return
    return js

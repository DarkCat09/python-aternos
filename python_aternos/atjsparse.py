"""Parsing and executing JavaScript code"""

import abc
import base64
import subprocess

from pathlib import Path
from typing import Optional, Union, Any
from typing import Type

import regex
import js2py

js: Optional['Interpreter'] = None


class Interpreter(abc.ABC):
    """Base JS interpreter class"""

    def __init__(self) -> None:
        pass

    def __getitem__(self, name: str) -> Any:
        return self.get_var(name)

    @abc.abstractmethod
    def exec_js(self, func: str) -> None:
        """Executes JavaScript code

        Args:
            func (str): JS function
        """
        pass

    @abc.abstractmethod
    def get_var(self, name: str) -> Any:
        """Returns JS variable value
        from the interpreter

        Args:
            name (str): Variable name

        Returns:
            Variable value
        """
        pass


class NodeInterpreter(Interpreter):

    def __init__(self, node: Union[str, Path]) -> None:
        super().__init__()
        self.proc = subprocess.Popen(
            node,
            stdout=subprocess.PIPE,
        )
    
    def exec_js(self, func: str) -> None:
        self.proc.communicate(func.encode('utf-8'))
    
    def get_var(self, name: str) -> Any:
        assert self.proc.stdout is not None
        self.proc.stdout.read()
        self.proc.communicate(name.encode('utf-8'))
        return self.proc.stdout.read().decode('utf-8')
    
    def __del__(self) -> None:
        self.proc.terminate()


class Js2PyInterpreter(Interpreter):

    # Thanks to http://regex.inginf.units.it
    arrowexp = regex.compile(r'\w[^\}]*+')

    def __init__(self) -> None:

        super().__init__()

        ctx = js2py.EvalJs({'atob': atob})
        ctx.execute('window.document = { };')
        ctx.execute('window.Map = function(_i){ };')
        ctx.execute('window.setTimeout = function(_f,_t){ };')
        ctx.execute('window.setInterval = function(_f,_t){ };')
        ctx.execute('window.encodeURIComponent = function(_s){ };')

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
    Decodes base64 string

    Args:
        s (str): Encoded data

    Returns:
        Decoded string
    """

    return base64.standard_b64decode(str(s)).decode('utf-8')


def get_interpreter(create: Type[Interpreter] = Js2PyInterpreter) -> 'Interpreter':
    global js
    if js is None:
        js = create()
    return js
